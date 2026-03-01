from django.shortcuts import render, redirect, get_object_or_404
from .models import Project
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
import stl
import numpy as np

def main_page(request):
    return render(request, 'main/index.html')


# views.py

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
                
                # ИСПОЛЬЗУЕМ float() чтобы превратить numpy.float в обычный float
                volume_cm3 = float(max(0, volume / 1000.0))

                # Приводим координаты к обычному float
                dims = {
                    'x': float(round(mesh.x.max() - mesh.x.min(), 2)),
                    'y': float(round(mesh.y.max() - mesh.y.min(), 2)),
                    'z': float(round(mesh.z.max() - mesh.z.min(), 2))
                }

                project.model_data = {
                    'volume': round(volume_cm3, 2),
                    'dimensions': dims,
                    'polygons': int(len(mesh.vectors)) # Приводим к int
                }
                project.status = 'ready'
            except Exception as e:
                print(f"Ошибка анализа STL: {e}")
                project.status = 'error'

        if project.model_data and 'volume' in project.model_data:
            results = calculate_project_costs(project, density, price_per_kg, infill)
            if results:
                project.total_price = int(results['total'])
                
                # Снова следим, чтобы в JSON уходили только стандартные типы
                project.model_data.update({
                    'weight': float(results['weight']),
                    'cost': float(results['cost'])
                })

        project.title = title
        project.save()
        return redirect('calculate_with_id', project_id=project.id)

    return render(request, 'main/calculate.html', {'project': project})


def register(request):
    return render(request, 'main/register.html')


def login(request):
    if request.method == 'POST':
        # Забираем данные из формы
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # Проверяем пользователя
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            auth_login(request, user) # Входим в аккаунт
            return redirect('myprojects') # Отправляем к проектам
        else:
            # Если данные неверны
            return render(request, 'main/login.html', {'error': 'Неверный логин или пароль'})
            
    return render(request, 'main/login.html')


def projects_list(request):
    # Получаем проекты только текущего пользователя (согласно ТЗ)
    if request.user.is_authenticated:
        projects = Project.objects.filter(user=request.user)
    else:
        projects = []
    return render(request, 'main/projects_list.html', {'projects': projects})

def calculate_project_costs(project, density, price_per_kg, infill):
    """
    Функция берет сохраненный объем из model_data и считает итоговые показатели.
    """
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