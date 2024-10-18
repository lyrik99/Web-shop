from django.shortcuts import redirect, render, get_object_or_404
from shop.models import Product
from .cart import Cart
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError

@transaction.atomic
@login_required
def cart_add(request, product_id):
    """Добавление товара в корзину."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        cart.add(product)
        messages.success(request, f'{product.name} добавлен в корзину')
    except ValueError:
        messages.error(request, 'Недостаточно товара на складе')
    return redirect('cart:cart_detail')

@transaction.atomic
@login_required
def cart_remove(request, product_id):
    """Удаление товара из корзины."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'{product.name} удален из корзины')
    return redirect('cart:cart_detail')

@transaction.atomic
@login_required
def cart_update(request, product_id):
    """Обновление количества товара в корзине."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    try:
        cart.update(product, quantity)
        messages.success(request, f'Количество товара {product.name} обновлено')
    except ValueError:
        messages.error(request, 'Недостаточно товара на складе')
    return redirect('cart:cart_detail')

@login_required
def cart_detail(request):
    """Отображение корзины."""
    cart = Cart(request)
    cart_total = cart.get_total_price()
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'cart_total': cart_total})

@login_required
@transaction.atomic
def cart_checkout(request):
    """Оформление заказа из корзины."""
    cart = Cart(request)
    if not cart:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('cart:cart_detail')

    # Создание заказа
    try:
        order = Order.objects.create(
            user=request.user,
            total=cart.get_total_price(),
            status='в обработке'
        )

        # Перенос товаров из корзины в заказ без повторного списания со склада
        for item in cart:
            product = item['product']
            quantity = item['quantity']

            # Создание OrderItem, но без уменьшения product.stock
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=item['price']
            )
            # Здесь не уменьшаем product.stock, так как это уже сделано при добавлении в корзину

        # Очищаем корзину после оформления заказа
        cart.clear()

        messages.success(request, 'Ваш заказ успешно оформлен!')
        return redirect('accounts:purchase_history')

    except IntegrityError as e:
        print(f'Ошибка оформления заказа: {e}')
        messages.error(request, 'Произошла ошибка при оформлении заказа.')
        return redirect('cart:cart_detail')

