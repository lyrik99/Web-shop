from django.urls import path
from .views import register_view, login_view  # Убедитесь, что здесь правильно импортируются представления

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),  # Путь для страницы входа
]
