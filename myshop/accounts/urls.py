from django.urls import path
from .views import register_view, login_view
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('register/', views.register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
]
