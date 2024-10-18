from django.test import TestCase
from django.urls import reverse
from shop.models import Product
from django.contrib.auth.models import User

class ProductViewsTest(TestCase):

    def test_product_list_view(self):
        """Проверка отображения списка продуктов."""
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_list.html')
