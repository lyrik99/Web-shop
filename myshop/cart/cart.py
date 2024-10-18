from decimal import Decimal
from django.conf import settings
from shop.models import Product

class Cart:
    def __init__(self, request):
        """Инициализация корзины."""
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """Добавление товара в корзину или обновление количества."""
        product_id = str(product.id)
        if product_id not in self.cart:
            # Если товара нет в корзине, добавляем его с указанным количеством
            if product.stock >= quantity:
                self.cart[product_id] = {
                    'quantity': quantity,
                    'price': str(product.price),
                }
                product.stock -= quantity
                product.save()
            else:
                raise ValueError("Not enough stock")
        else:
            # Если товар уже в корзине
            if update_quantity:
                new_quantity = quantity
            else:
                new_quantity = self.cart[product_id]['quantity'] + quantity

            if product.stock >= (new_quantity - self.cart[product_id]['quantity']):
                product.stock -= (new_quantity - self.cart[product_id]['quantity'])
                self.cart[product_id]['quantity'] = new_quantity
                product.save()
            else:
                raise ValueError("Not enough stock")
        self.save()

    def remove(self, product):
        """Удаление товара из корзины."""
        product_id = str(product.id)
        if product_id in self.cart:
            # Возвращаем товар на склад
            product.stock += self.cart[product_id]['quantity']
            product.save()
            del self.cart[product_id]
            self.save()

    def update(self, product, quantity):
        """Обновление количества товара в корзине."""
        product_id = str(product.id)
        if product_id in self.cart:
            current_quantity = self.cart[product_id]['quantity']
            if product.stock + current_quantity >= quantity:
                product.stock += current_quantity - quantity
                self.cart[product_id]['quantity'] = quantity
                product.save()
            else:
                raise ValueError("Not enough stock")
            self.save()

    def save(self):
        """Сохранение изменений в сессии."""
        self.session['cart'] = self.cart
        self.session.modified = True

    def __iter__(self):
        """Итерация по товарам в корзине."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Возвращает общее количество товаров в корзине."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Возвращает общую стоимость всех товаров в корзине."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Очистка корзины."""
        self.session.pop('cart', None)
        self.session.modified = True

    def is_empty(self):
        """Проверка на пустую корзину."""
        return not bool(self.cart)
