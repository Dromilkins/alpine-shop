from django.db import models
from django.conf import settings
from shop.models import Product

class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        UNPAID = 'unpaid', 'Не оплачено'
        PAID = 'paid', 'Оплачено'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает оплаты'
        NEW = 'new', 'Новый'
        PROCESSING = 'processing', 'В обработке'
        SHIPPED = 'shipped', 'Отправлен'
        DELIVERED = 'delivered', 'Доставлен'
        CANCELED = 'canceled', 'Отменён'

    DELIVERY_METHOD = [
        ('courier', 'Курьер'),
        ('pickup', 'Самовывоз'),
        ('post', 'Почта'),
    ]

    PAYMENT_METHOD = [
        ('card', 'Банковская карта'),
        ('cash', 'Наличные'),
        ('online', 'Онлайн оплата (ЮMoney)'),
    ]

    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.TextField(verbose_name='Адрес')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    delivery_method = models.CharField(max_length=50, choices=DELIVERY_METHOD, default='courier', verbose_name='Способ доставки')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, default='cash', verbose_name='Способ оплаты')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name='Статус')
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID, verbose_name='Статус оплаты')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлён')
    is_paid = models.BooleanField(default=False, verbose_name='Оплачен')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата оплаты')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='orders',verbose_name='Пользователь')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Сумма скидки')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created']

    def __str__(self):
        return f'Заказ №{self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name='Товар')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    def __str__(self):
        return f'{self.id} - {self.product.name}'

    def get_cost(self):
        return self.price * self.quantity