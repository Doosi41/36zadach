from django.db import migrations, models
from django.contrib.auth.models import User

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    
    title = models.CharField(max_length=255, verbose_name="Название проекта")
    client_name = models.CharField(max_length=255, blank=True, null=True)
    contact_info = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='projects/')
    
    # Весь сок здесь
    
    technology = models.CharField(max_length=50, default='FDM')
    material_density = models.FloatField(default=1.25)
    material_cost_per_kg = models.FloatField(default=2000)
    fill_percentage = models.IntegerField(default=20)
    print_time_hours = models.FloatField(default=0)
    
    # Результаты расчетов
    total_weight = models.FloatField(default=0)
    total_price = models.IntegerField(default=0)
    final_price = models.FloatField(default=0)
    ai_description = models.TextField(blank=True, null=True)
    

    model_file = models.FileField(upload_to='models/%Y/%m/%d/', blank=True, null=True)
    
    model_data = models.JSONField(default=dict, blank=True)
    
    parameters = models.JSONField(default=dict, blank=True)
    
    # Тут храним объем, габариты и полигоны
    model_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default='pending')
    
    # Подсчет стоимости
    density = models.FloatField(default=1.25)
    infill = models.IntegerField(default=20)
    
    # Производство
    technology = models.CharField(max_length=50, default='FDM')
    material_name = models.CharField(max_length=100, default='PLA')
    
    # Временные затраты (в часах)
    print_time = models.FloatField(default=0)
    post_processing_time = models.FloatField(default=0)
    modeling_time = models.FloatField(default=0)
    
    # Экономика
    quantity = models.IntegerField(default=1)
    markup_coefficient = models.FloatField(default=2.5) # Коэффициент наценки
    defect_rate = models.FloatField(default=5.0) # Вероятность брака в %
    tax_rate = models.FloatField(default=0) # Налог в %
    
    # Доп. расходы
    energy_cost = models.FloatField(default=5.5) # руб/кВт
    depreciation = models.FloatField(default=10.0) # амортизация в час
    
    # Интерфейс
    currency = models.CharField(max_length=10, default='RUB')
    language = models.CharField(max_length=10, default='RU')
    
    ai_description = models.TextField(blank=True, null=True, verbose_name="Описание от ИИ")
    ai_commercial_text = models.TextField(blank=True, null=True, verbose_name="Коммерческое предложение")

    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Ожидание'), ('processing', 'Обработка'), ('ready', 'Готово'), ('error', 'Ошибка')],
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"