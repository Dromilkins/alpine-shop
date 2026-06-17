from django.db import models
from django.urls import reverse
from django.conf import settings
class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, verbose_name='Изображение')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    available = models.BooleanField(default=True, verbose_name='Доступен')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлён')
    stock = models.PositiveIntegerField(default=0, verbose_name='Остаток на складе')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])

    brand = models.CharField(max_length=100, blank=True, verbose_name='Бренд')
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Вес (г)')
    material = models.CharField(max_length=100, blank=True, verbose_name='Материал')
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Начинающий'),
            ('intermediate', 'Средний'),
            ('advanced', 'Профессиональный'),
            ('expert', 'Экспертный'),
        ],
        blank=True,
        verbose_name='Уровень'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['brand']),  # для быстрого поиска по бренду
            models.Index(fields=['price']),  # для сортировки по цене
        ]

    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Вес (г)')
    material = models.CharField(max_length=100, blank=True, verbose_name='Материал')

    # Класс прочности
    STRENGTH_CLASS = [
        ('basic', 'Базовый'),
        ('intermediate', 'Средний'),
        ('professional', 'Профессиональный'),
        ('expert', 'Экспертный'),
    ]
    strength_class = models.CharField(max_length=20, choices=STRENGTH_CLASS, blank=True, verbose_name='Класс прочности')

    # Тип застёжки (для карабинов, обвязок)
    CLASP_TYPE = [
        ('screw', 'Винтовая муфта'),
        ('auto', 'Автомуфта'),
        ('bayonet', 'Байонетная'),
        ('none', 'Без муфты'),
    ]
    clasp_type = models.CharField(max_length=20, choices=CLASP_TYPE, blank=True, verbose_name='Тип застёжки')

    # Диапазон температур (для одежды, спальников)
    temp_min = models.IntegerField(null=True, blank=True, verbose_name='Мин. температура (°C)')
    temp_max = models.IntegerField(null=True, blank=True, verbose_name='Макс. температура (°C)')

    # Дополнительные специфичные поля
    length = models.IntegerField(null=True, blank=True, verbose_name='Длина (см)')
    load_capacity = models.IntegerField(null=True, blank=True, verbose_name='Грузоподъёмность (кг)')


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    excerpt = models.TextField(verbose_name='Краткое описание', help_text='Отображается в списке статей')
    content = models.TextField(verbose_name='Полный текст')
    image = models.ImageField(upload_to='articles/%Y/%m/%d/', blank=True, verbose_name='Изображение')
    author = models.CharField(max_length=100, default='ALPGEAR Team', verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:article_detail', args=[self.slug])


class Subscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')
    discount_used = models.BooleanField(default=False, verbose_name='Скидка использована')
    discount_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Код скидки')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return self.email

    def generate_discount_code(self):
        import hashlib
        import time
        code = hashlib.md5(f"{self.email}{time.time()}".encode()).hexdigest()[:8].upper()
        self.discount_code = code
        self.save()
        return code


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'product']  # один отзыв на товар от одного пользователя

    def __str__(self):
        return f'{self.user.username} - {self.product.name} - {self.rating}★'