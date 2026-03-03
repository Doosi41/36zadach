import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from google import genai
from google.genai import types
import stl
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login

from .models import Project

def main_page(request):
    return render(request, 'main/index.html')

@login_required
def calculate(request, project_id=None):
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title', 'Новый проект')
        model_file = request.FILES.get('model_file')
        density = request.POST.get('density', 1.25)
        price_per_kg = request.POST.get('price_per_kg', 2500)
        infill = request.POST.get('infill', 20)

        if not project:
            project = Project.objects.create(user=request.user, title=title)
        
        if model_file:
            project.model_file = model_file
            project.save()
            
            try:
                mesh = stl.mesh.Mesh.from_file(project.model_file.path)
                volume, _, _ = mesh.get_mass_properties()
                volume_cm3 = float(max(0, volume / 1000.0))

                dims = {
                    'x': float(round(mesh.x.max() - mesh.x.min(), 2)),
                    'y': float(round(mesh.y.max() - mesh.y.min(), 2)),
                    'z': float(round(mesh.z.max() - mesh.z.min(), 2))
                }

                project.model_data = {
                    'volume': round(volume_cm3, 2),
                    'dimensions': dims,
                    'polygons': int(len(mesh.vectors))
                }
                project.status = 'ready'
            except Exception as e:
                print(f"Ошибка анализа STL: {e}")
                project.status = 'error'

        if project.model_data and 'volume' in project.model_data:
            results = calculate_project_costs(project, density, price_per_kg, infill)
            if results:
                project.total_price = int(results['total'])
                project.model_data.update({
                    'weight': float(results['weight']),
                    'cost': float(results['cost'])
                })

        project.title = title
        project.save()
        return redirect('calculate_with_id', project_id=project.id)

    return render(request, 'main/calculate.html', {'project': project})

def calculate_project_costs(project, density, price_per_kg, infill):
    volume_cm3 = project.model_data.get('volume', 0)
    if volume_cm3 > 0:
        weight_g = volume_cm3 * float(density) * (int(infill) / 100)
        cost_rub = (weight_g / 1000) * float(price_per_kg)
        total_price = round(cost_rub * 2.5) 
        return {
            'weight': round(weight_g, 2),
            'cost': round(cost_rub, 2),
            'total': total_price
        }
    return None

def generate_ai_text(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    API_KEY = 'AIzaSyAT7pZQwnqsXKdYr4F1rbnDMdFkTRJUFXA'
    
    try:
        client = genai.Client(api_key=API_KEY)

        dim = project.model_data.get('dimensions', {'x': 0, 'y': 0, 'z': 0})
        
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

        # Вызываем генерацию
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        ai_result = response.parsed if hasattr(response, 'parsed') else json.loads(response.text)

        # Сохранение в базу
        if not project.model_data:
            project.model_data = {}
        
        project.model_data['ai_description'] = ai_result.get('description')
        project.model_data['ai_commercial'] = ai_result.get('commercial')
        project.save()

        return JsonResponse({'status': 'success', 'data': ai_result})

    except Exception as e:
        print(f"--- ОШИБКА AI --- \n{str(e)}")
        return JsonResponse({
            'status': 'error', 
            'message': f"Ошибка API: {str(e)}"
        }, status=500)
        
        

def register(request):
    return render(request, 'main/register.html')

def login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            auth_login(request, user)
            return redirect('myprojects')
        return render(request, 'main/login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'main/login.html')

def projects_list(request):
    projects = Project.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'main/projects_list.html', {'projects': projects})