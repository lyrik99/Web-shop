from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from shop.models import Product
from .cart import Cart
from .models import Order, OrderItem


class CartTest(TestCase):

    def setUp(self):
        # Создаем пользователя для тестов
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

        # Создаем продукт для тестирования с указанием владельца
        self.product = Product.objects.create(
            name='Test Product',
            price=10.0,
            stock=5,
            owner=self.user  # Указываем владельца
        )

    def test_cart_add(self):
        """Проверка добавления товара в корзину."""
        response = self.client.post(reverse('cart:cart_add', args=[self.product.id]))
        self.assertRedirects(response, reverse('cart:cart_detail'))  # Проверка перенаправления
        cart = Cart(self.client)
        self.assertEqual(len(cart), 1)  # Проверяем, что товар добавлен
        self.assertEqual(cart.get_total_price(), 10.0)  # Проверяем общую стоимость


    def test_cart_remove(self):
        """Проверка удаления товара из корзины."""
        self.client.post(reverse('cart:cart_add', args=[self.product.id]))  # Сначала добавляем продукт
        response = self.client.post(reverse('cart:cart_remove', args=[self.product.id]))
        self.assertRedirects(response, reverse('cart:cart_detail'))  # Проверка перенаправления
        cart = Cart(self.client)
        self.assertEqual(len(cart), 0)  # Проверяем, что корзина пуста

    def test_cart_update(self):
        """Проверка обновления количества товара в корзине."""
        self.client.post(reverse('cart:cart_add', args=[self.product.id]))  # Сначала добавляем продукт
        response = self.client.post(reverse('cart:cart_update', args=[self.product.id]), {'quantity': 3})
        self.assertRedirects(response, reverse('cart:cart_detail'))  # Проверка перенаправления
        cart = Cart(self.client)
        self.assertEqual(cart.get_total_price(), 30.0)  # Проверяем, что количество обновлено


    def test_cart_detail(self):
        """Проверка отображения корзины."""
        self.client.post(reverse('cart:cart_add', args=[self.product.id]))  # Сначала добавляем продукт
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)  # Проверка доступности страницы
        self.assertContains(response, 'Test Product')  # Проверка, что продукт отображается в корзине

    def test_cart_checkout(self):
        """Проверка оформления заказа из корзины."""
        self.client.post(reverse('cart:cart_add', args=[self.product.id]))  # Сначала добавляем продукт
        response = self.client.post(reverse('cart:cart_checkout'))
        self.assertRedirects(response, reverse('accounts:purchase_history'))  # Проверка перенаправления
        self.assertEqual(Order.objects.count(), 1)  # Проверяем, что заказ создан
        self.assertEqual(Order.objects.first().total, 10.0)  # Проверяем, что общая сумма заказа корректна

