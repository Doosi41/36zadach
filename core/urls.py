from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('project/<int:project_id>/generate_ai/', views.generate_ai_text, name='generate_ai_text'),
]