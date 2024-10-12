from django.urls import path
from . import views

app_name = 'cart'  # Пространство имен для маршрутов корзины

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),  # Маршрут для просмотра корзины
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),  # Маршрут для добавления в корзину
]
