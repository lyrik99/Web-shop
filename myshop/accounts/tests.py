from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsTest(TestCase):

    def setUp(self):
        # Создаем пользователя для тестов
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_user_profile_view(self):
        """Проверка доступа к профилю пользователя."""
        response = self.client.get(reverse('accounts:user_profile'))
        self.assertRedirects(response, reverse('accounts:purchase_history'))

    def test_register_view(self):
        """Проверка регистрации нового пользователя."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })
        self.assertRedirects(response, reverse('product_list'))  # Проверяем, что перенаправляет на список продуктов
        self.assertTrue(User.objects.filter(username='newuser').exists())  # Убедитесь, что пользователь создан

    def test_logout_view(self):
        """Проверка выхода из системы."""
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))  # Проверяем, что перенаправляет на страницу входа

    def test_purchase_history_view(self):
        """Проверка доступа к истории покупок."""
        response = self.client.get(reverse('accounts:purchase_history'))
        self.assertEqual(response.status_code, 200)  # Проверяем, что страница доступна
