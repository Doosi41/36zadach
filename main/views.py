import json
import logging
from functools import lru_cache

import numpy as np
import stl
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from google import genai
from google.genai import types

from .models import Project

log = logging.getLogger(__name__)


def main_page(request):
    return render(request, 'main/index.html')


def _number(value, default, minimum=0.0):
    """Число из формы; пустое, кривое или меньше minimum → default."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if number >= minimum else default


def analyze_stl(path):
    """Объём (см³), габариты (мм) и число полигонов STL-модели."""
    triangles = stl.mesh.Mesh.from_file(path).vectors.astype(np.float64)
    if not len(triangles):
        raise ValueError('В STL нет треугольников')
    # Объём — сумма знаковых объёмов тетраэдров (v0·(v1×v2))/6. Так в ~100 раз
    # быстрее get_mass_properties(), который ещё и проверяет замкнутость сетки.
    # abs(): у модели с вывернутыми нормалями объём получается отрицательным.
    volume = abs(np.einsum('ij,ij->i', triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])).sum()) / 6
    points = triangles.reshape(-1, 3)
    x, y, z = (points.max(axis=0) - points.min(axis=0)).round(2).tolist()
    return {
        'volume': round(float(volume) / 1000.0, 2),
        'dimensions': {'x': x, 'y': y, 'z': z},
        'polygons': len(triangles),
    }


@login_required
def calculate(request, project_id=None):
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'POST':
        if not project:
            project = Project(user=request.user, title=request.POST.get('title') or 'Новый проект')
        elif request.POST.get('title'):
            project.title = request.POST['title']

        project.technology = request.POST.get('technology') or project.technology
        project.density = _number(request.POST.get('density'), project.density)
        project.material_cost_per_kg = _number(request.POST.get('price_per_kg'), project.material_cost_per_kg)
        project.markup_coefficient = _number(request.POST.get('markup'), project.markup_coefficient, minimum=1)

        model_file = request.FILES.get('model_file')
        if model_file:
            # Старый файл удаляем, иначе каждая перезагрузка копит копию в media/
            if project.model_file:
                project.model_file.delete(save=False)
            project.model_file.save(model_file.name, model_file, save=False)
            try:
                project.model_data = {**project.model_data, **analyze_stl(project.model_file.path)}
                project.status = 'ready'
            except Exception:
                log.exception('Не удалось разобрать STL %s', project.model_file.name)
                project.status = 'error'

        results = calculate_project_costs(project)
        if results:
            project.total_weight = results['weight']
            project.total_price = results['total']
            project.model_data.update(weight=results['weight'], cost=results['cost'])

        project.save()
        return redirect('calculate_with_id', project_id=project.id)

    return render(request, 'main/calculate.html', {'project': project})


def calculate_project_costs(project):
    volume_cm3 = (project.model_data or {}).get('volume', 0)
    if volume_cm3 <= 0:
        return None
    weight_g = volume_cm3 * project.density * (project.infill / 100)
    cost = (weight_g / 1000) * project.material_cost_per_kg
    return {
        'weight': round(weight_g, 2),
        'cost': round(cost, 2),
        'total': round(cost * project.markup_coefficient),
    }


@lru_cache(maxsize=1)
def _gemini_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)


@login_required
@require_POST
def generate_ai_text(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if not settings.GEMINI_API_KEY:
        return JsonResponse({'status': 'error', 'message': 'GEMINI_API_KEY не задан'}, status=503)

    dim = (project.model_data or {}).get('dimensions', {'x': 0, 'y': 0, 'z': 0})
    prompt = f"""
    Ты эксперт в 3D печати. Напиши коммерческое предложение для детали:
    Название: {project.title}
    Габариты: {dim.get('x')} x {dim.get('y')} x {dim.get('z')} мм
    Технология: {project.technology or 'FDM'}

    Ответь СТРОГО в формате JSON:
    {{
        "description": "краткое описание",
        "commercial": "текст предложения"
    }}
    """

    try:
        response = _gemini_client().models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type='application/json'),
        )
        ai_result = json.loads(response.text)
        ai_result = {
            'description': str(ai_result.get('description', '')),
            'commercial': str(ai_result.get('commercial', '')),
        }
    except Exception:
        log.exception('Gemini не ответил для проекта %s', project.id)
        return JsonResponse({'status': 'error', 'message': 'AI не ответил, попробуйте ещё раз'}, status=502)

    project.model_data = {
        **(project.model_data or {}),
        'ai_description': ai_result['description'],
        'ai_commercial': ai_result['commercial'],
    }
    project.save(update_fields=['model_data'])
    return JsonResponse({'status': 'success', 'data': ai_result})


def register(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            error = 'Заполните имя и пароль'
        elif User.objects.filter(username__iexact=username).exists():
            error = 'Это имя уже занято'
        else:
            try:
                validate_password(password, User(username=username))
            except ValidationError as e:
                error = ' '.join(e.messages)
            else:
                user = User.objects.create_user(username=username, password=password)
                auth_login(request, user)
                return redirect('projects')
    return render(request, 'main/register.html', {'error': error})


def login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            auth_login(request, user)
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                    next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('projects')
        return render(request, 'main/login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'main/login.html')


@login_required
def projects_list(request):
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/projects_list.html', {'projects': projects})
