from django.urls import path
from django.contrib.auth import views as auth_views 
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.main_page, name='main'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('projects/', views.projects_list, name='myprojects'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('calculate/', views.calculate, name='calculate'),
    path('calculate/<int:project_id>/', views.calculate, name='calculate_with_id'),
] + static(settings.MEDIA_URL, document_address=settings.MEDIA_ROOT)