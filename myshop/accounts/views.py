from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from cart.models import CartItem, Order, OrderItem
from django.contrib import messages
from django.db import transaction

@transaction.atomic
@login_required
def user_profile(request):
    # Получение товаров в корзине для текущего пользователя
    cart_items = CartItem.objects.filter(user=request.user)

    # Получение истории заказов для текущего пользователя
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return redirect('accounts:purchase_history')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматически входить после регистрации
            return redirect('product_list')  # Перенаправление на страницу списка продуктов
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:user_profile')  # Перенаправление на профиль
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)  # Выход пользователя
    return redirect('accounts:login')  # Перенаправление на страницу входа

@transaction.atomic
@login_required
def purchase_history(request):
    """Отображение истории покупок пользователя."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/purchase_history.html', {'orders': orders})

@transaction.atomic
@login_required
def order_detail(request, order_id):
    """Отображение деталей конкретного заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'accounts/order_detail.html', {'order': order})

@transaction.atomic
def cancel_order(request, order_id):
    """Отмена заказа и восстановление количества товара"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'в обработке':
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            product = item.product
            product.stock += item.quantity
            product.save()

        order.status = 'отменен'
        order.save()

        messages.success(request, 'Ваш заказ был успешно отменен, а товары возвращены на склад')
    else:
        messages.error(request, 'Этот заказ уже нельзя отменить')

    return redirect('accounts:purchase_history')

@transaction.atomic
@login_required
def delete_order(request, order_id):
    """Удаление заказа со статусом 'Отменен'"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'отменен':
        order.delete()  # Удаляем заказ
        messages.success(request, 'Заказ успешно удален из истории')
    else:
        messages.error(request, 'Вы можете удалить только отмененные заказы')

    return redirect('accounts:purchase_history')