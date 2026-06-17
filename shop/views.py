from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from pyexpat.errors import messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from .forms import ReviewForm
from .models import *
from cart.forms import CartAddProductForm
from .models import Subscriber
from django.http import JsonResponse
import json
from django.db.models import Q
from .models import Category, Product

def subscribe(request):
    """Подписка на рассылку через AJAX"""
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email or '@' not in email:
            return JsonResponse({'status': 'error', 'message': 'Введите корректный email'})

        try:
            subscriber, created = Subscriber.objects.get_or_create(email=email)

            if created:
                # Новый подписчик - генерируем код скидки
                discount_code = subscriber.generate_discount_code()

                # Сохраняем код в сессию
                request.session['discount_code'] = discount_code
                request.session['discount_email'] = email
                request.session.modified = True

                return JsonResponse({
                    'status': 'success',
                    'message': f'Подписка оформлена! Ваш код скидки 10%: {discount_code}',
                    'discount_code': discount_code
                })
            else:
                if not subscriber.discount_used and subscriber.discount_code:
                    request.session['discount_code'] = subscriber.discount_code
                    request.session.modified = True
                    return JsonResponse({
                        'status': 'success',
                        'message': f'Вы уже подписаны. Ваш код скидки: {subscriber.discount_code}',
                        'discount_code': subscriber.discount_code
                    })
                elif subscriber.discount_used:
                    return JsonResponse({'status': 'error', 'message': 'Вы уже использовали скидку на первый заказ'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Вы уже подписаны на рассылку'})

        except Exception as e:
            print(f"Subscribe error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Ошибка при подписке'})

    return JsonResponse({'status': 'error', 'message': 'Метод не поддерживается'})

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # ----- УМНЫЙ ПОИСК -----
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )

    # ----- ФИЛЬТРАЦИЯ -----
    # Цена
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Вес
    min_weight = request.GET.get('min_weight')
    max_weight = request.GET.get('max_weight')
    if min_weight:
        products = products.filter(weight__gte=min_weight)
    if max_weight:
        products = products.filter(weight__lte=max_weight)

    # Материал
    material = request.GET.get('material')
    if material:
        products = products.filter(material__icontains=material)

    # Класс прочности
    strength_class = request.GET.get('strength_class')
    if strength_class:
        products = products.filter(strength_class=strength_class)

    # Тип застёжки
    clasp_type = request.GET.get('clasp_type')
    if clasp_type:
        products = products.filter(clasp_type=clasp_type)

    # Бренд
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand=brand)

    # ----- СОРТИРОВКА -----
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    elif sort_by == 'weight_asc':
        products = products.order_by('weight')
    elif sort_by == 'weight_desc':
        products = products.order_by('-weight')

    # ----- ПАГИНАЦИЯ (ПОСЛЕ ВСЕХ ФИЛЬТРОВ)-----
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    # Уникальные значения для фильтров
    brands = Product.objects.filter(available=True).exclude(brand__isnull=True).exclude(brand='').values_list('brand',
                                                                                                              flat=True).distinct()
    materials = Product.objects.filter(available=True).exclude(material='').values_list('material',
                                                                                        flat=True).distinct()

    # Список товаров для сравнения (из сессии)
    compare_ids = request.session.get('compare_ids', [])
    compare_products = Product.objects.filter(id__in=compare_ids)

    context = {
        'category': category,
        'categories': categories,
        'products': products_page,  # ← страница с товарами
        'brands': sorted(set(brands)),
        'materials': sorted(set(materials)),
        'current_filters': {
            'search': search_query,
            'min_price': min_price,
            'max_price': max_price,
            'min_weight': min_weight,
            'max_weight': max_weight,
            'material': material,
            'strength_class': strength_class,
            'clasp_type': clasp_type,
            'brand': brand,
            'sort': sort_by,
        },
        'compare_products': compare_products,
        'compare_count': len(compare_ids),
    }
    return render(request, 'shop/product/list.html', context)

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)

    # Максимальное количество = остаток на складе
    max_qty = product.stock if product.stock > 0 else 20
    cart_product_form = CartAddProductForm(max_quantity=max_qty)

    has_purchased = False
    existing_review = None

    if request.user.is_authenticated:
        has_purchased = Order.objects.filter(
            user=request.user,
            items__product=product,
            is_paid=True
        ).exists()
        existing_review = Review.objects.filter(user=request.user, product=product).first()

    context = {
        'product': product,
        'cart_product_form': cart_product_form,
        'has_purchased': has_purchased,
        'existing_review': existing_review,
    }
    return render(request, 'shop/product/detail.html', context)

def mountain_map(request):
    """3D карта горы с интерактивными маркерами товаров"""
    products = Product.objects.filter(available=True)

    # Координаты товаров на горе (можно настроить под каждую категорию)
    product_positions = []

    # Категории и их позиции
    positions_by_category = {
        'ledoruby': (-2, 3.2, 1.5),
        'obvyazki': (0, 1.2, 2.8),
        'karabiny': (1.5, 2.5, 1.8),
        'verevki': (2.5, 2.0, 0.5),
        'kaski': (-1.2, 1.8, 2.2),
        'koshki': (-2.5, 1.5, -1),
        'zhumary': (3, 1.8, -0.5),
        'ottyazhki': (0.5, 2.2, 2.5),
        'ryukzaki': (-1.5, 0.8, 2),
        'odezhda': (2, 3.5, -1.5),
    }

    for product in products:
        category_slug = product.category.slug
        if category_slug in positions_by_category:
            x, y, z = positions_by_category[category_slug]
        else:
            # Случайная позиция, если категория не задана
            x = (hash(product.slug) % 50 - 25) / 10
            z = (hash(product.slug + 'z') % 40 - 20) / 10
            y = abs(x) * 0.5 + 1

        product_positions.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'description': product.description,
            'slug': product.slug,
            'position_x': x,
            'position_y': y + 1.2,
            'position_z': z,
            'category': category_slug
        })

    context = {
        'products_json': json.dumps(product_positions, ensure_ascii=False)
    }
    return render(request, 'shop/3d_map.html', context)

def home(request):
    """Главная страница"""
    categories = Category.objects.all()
    popular_products = Product.objects.filter(available=True)[:8]

    context = {
        'categories': categories,
        'popular_products': popular_products,
    }
    return render(request, 'shop/home.html', context)

def article_list(request):
    """Список статей (журнал)"""
    articles = Article.objects.filter(is_published=True)
    return render(request, 'shop/article_list.html', {'articles': articles})

def article_detail(request, slug):
    """Детальная страница статьи"""
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, 'shop/article_detail.html', {'article': article})

def add_to_compare(request, product_id):
    """Добавление товара в сравнение"""
    compare_ids = request.session.get('compare_ids', [])

    if product_id not in compare_ids and len(compare_ids) < 4:
        compare_ids.append(product_id)
        request.session['compare_ids'] = compare_ids
        messages.success(request, 'Товар добавлен к сравнению')
    elif product_id in compare_ids:
        messages.info(request, 'Товар уже в списке сравнения')
    else:
        messages.warning(request, 'Можно сравнить не более 4 товаров')

    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))

def remove_from_compare(request, product_id):
    """Удаление товара из сравнения"""
    compare_ids = request.session.get('compare_ids', [])
    if product_id in compare_ids:
        compare_ids.remove(product_id)
        request.session['compare_ids'] = compare_ids
        messages.success(request, 'Товар удалён из сравнения')

    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))

def compare_products(request):
    """Страница сравнения товаров"""
    compare_ids = request.session.get('compare_ids', [])
    products = Product.objects.filter(id__in=compare_ids, available=True)

    # Характеристики для сравнения
    attributes = ['brand', 'price', 'weight', 'material', 'strength_class', 'clasp_type']

    context = {
        'products': products,
        'attributes': attributes,
    }
    return render(request, 'shop/compare.html', context)

@login_required
def add_review(request, id, slug):
    product = get_object_or_404(Product, id=id, available=True)

    # Проверяем, покупал ли пользователь этот товар
    has_purchased = Order.objects.filter(
        user=request.user,
        items__product=product,
        is_paid=True
    ).exists()

    if not has_purchased:
        messages.error(request, 'Вы можете оставить отзыв только на купленный товар')
        return redirect('shop:product_detail', id=product.id, slug=product.slug)

    # Проверяем, не оставлял ли уже отзыв
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        messages.warning(request, 'Вы уже оставили отзыв на этот товар')
        return redirect('shop:product_detail', id=product.id, slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Отзыв успешно добавлен!')
            return redirect('shop:product_detail', id=product.id, slug=product.slug)
    else:
        form = ReviewForm()

    return render(request, 'shop/add_review.html', {'product': product, 'form': form})

@login_required
def user_reviews(request):
    """Страница с отзывами пользователя"""
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/user_reviews.html', {'reviews': reviews})