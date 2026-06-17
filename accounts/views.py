from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from decimal import Decimal
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from orders.models import Order, OrderItem
from shop.models import Category, Product, Article
from shop.forms import ProductForm, CategoryForm, ArticleForm
from orders.forms import OrderStatusForm
from decimal import Decimal
from django.db.models import Sum, F

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def is_admin(user):
    return user.is_superuser or user.is_staff


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('shop:product_list')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в аккаунт')
            next_url = request.GET.get('next', 'shop:product_list')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта')
    return redirect('home')


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Профиль успешно обновлён')
            return redirect('accounts:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'accounts/profile.html', context)


@login_required
def orders(request):
    orders_list = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'accounts/orders.html', {'orders': orders_list})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'accounts/order_detail.html', {'order': order})


# ==================== АДМИН-ПАНЕЛЬ ====================
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    stats = {
        'total_orders': Order.objects.count(),
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_articles': Article.objects.count(),
        'total_users': User.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'new_orders': Order.objects.filter(status='new').count(),
        # ВЫРУЧКА — считаем по позициям заказа
        'revenue': Order.objects.filter(is_paid=True).aggregate(
            total=Sum('items__price')
        )['total'] or Decimal('0'),
    }
    recent_orders = Order.objects.all().order_by('-created')[:10]
    return render(request, 'accounts/admin_dashboard.html', {'stats': stats, 'recent_orders': recent_orders})


# ==================== УПРАВЛЕНИЕ ТОВАРАМИ ====================
@login_required
@user_passes_test(is_admin)
def admin_products(request):
    products = Product.objects.all().order_by('-created')
    return render(request, 'accounts/admin_products.html', {'products': products})


@login_required
@user_passes_test(is_admin)
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно добавлен')
            return redirect('accounts:admin_products')
    else:
        form = ProductForm()
    return render(request, 'accounts/admin_product_form.html', {'form': form, 'title': 'Добавить товар'})


@login_required
@user_passes_test(is_admin)
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлён')
            return redirect('accounts:admin_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'accounts/admin_product_form.html', {'form': form, 'title': 'Редактировать товар'})


@login_required
@user_passes_test(is_admin)
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар удалён')
        return redirect('accounts:admin_products')
    return render(request, 'accounts/admin_confirm_delete.html', {'object': product, 'type': 'товар'})


# ==================== УПРАВЛЕНИЕ КАТЕГОРИЯМИ ====================
@login_required
@user_passes_test(is_admin)
def admin_categories(request):
    categories = Category.objects.all()
    return render(request, 'accounts/admin_categories.html', {'categories': categories})


@login_required
@user_passes_test(is_admin)
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно добавлена')
            return redirect('accounts:admin_categories')
    else:
        form = CategoryForm()
    return render(request, 'accounts/admin_category_form.html', {'form': form, 'title': 'Добавить категорию'})


@login_required
@user_passes_test(is_admin)
def admin_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория обновлена')
            return redirect('accounts:admin_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'accounts/admin_category_form.html', {'form': form, 'title': 'Редактировать категорию'})


@login_required
@user_passes_test(is_admin)
def admin_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Категория удалена')
        return redirect('accounts:admin_categories')
    return render(request, 'accounts/admin_confirm_delete.html', {'object': category, 'type': 'категорию'})


# ==================== УПРАВЛЕНИЕ ЗАКАЗАМИ ====================
@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'accounts/admin_orders.html', {'orders': orders})


@login_required
@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Статус заказа #{order.id} обновлён')
            return redirect('accounts:admin_orders')
    else:
        form = OrderStatusForm(instance=order)

    return render(request, 'accounts/admin_order_detail.html', {'order': order, 'form': form})


# ==================== УПРАВЛЕНИЕ СТАТЬЯМИ ====================
@login_required
@user_passes_test(is_admin)
def admin_articles(request):
    articles = Article.objects.all().order_by('-created_at')
    return render(request, 'accounts/admin_articles.html', {'articles': articles})


@login_required
@user_passes_test(is_admin)
def admin_article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья добавлена')
            return redirect('accounts:admin_articles')
    else:
        form = ArticleForm()
    return render(request, 'accounts/admin_article_form.html', {'form': form, 'title': 'Добавить статью'})


@login_required
@user_passes_test(is_admin)
def admin_article_edit(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья обновлена')
            return redirect('accounts:admin_articles')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'accounts/admin_article_form.html', {'form': form, 'title': 'Редактировать статью'})


@login_required
@user_passes_test(is_admin)
def admin_article_delete(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Статья удалена')
        return redirect('accounts:admin_articles')
    return render(request, 'accounts/admin_confirm_delete.html', {'object': article, 'type': 'статью'})


# ==================== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ====================
@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/admin_users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def admin_user_reset_password(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Проверка длины
        if len(new_password) < 8:
            messages.error(request, 'Пароль должен содержать минимум 8 символов')
        elif new_password != confirm_password:
            messages.error(request, 'Пароли не совпадают')
        else:
            target_user.password = make_password(new_password)
            target_user.save()
            messages.success(request, f'Пароль для {target_user.username} успешно изменён')
            return redirect('accounts:admin_users')

    return render(request, 'accounts/admin_user_reset_password.html', {'target_user': target_user})


@login_required
@user_passes_test(is_admin)
def admin_user_delete(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    if target_user.id == request.user.id:
        messages.error(request, 'Нельзя удалить самого себя')
        return redirect('accounts:admin_users')

    if target_user.is_superuser:
        messages.error(request, 'Нельзя удалить администратора')
        return redirect('accounts:admin_users')

    username = target_user.username
    target_user.delete()
    messages.success(request, f'Пользователь {username} удалён')
    return redirect('accounts:admin_users')


@login_required
@user_passes_test(is_admin)
def admin_user_delete(request, user_id):
    """Удаление пользователя (админ-функция)"""
    target_user = get_object_or_404(User, id=user_id)

    # Не даём удалить самого себя
    if target_user.id == request.user.id:
        messages.error(request, 'Нельзя удалить самого себя')
        return redirect('accounts:admin_users')

    # Не даём удалить суперпользователя
    if target_user.is_superuser:
        messages.error(request, 'Нельзя удалить администратора')
        return redirect('accounts:admin_users')

    username = target_user.username
    target_user.delete()
    messages.success(request, f'Пользователь {username} удалён')
    return redirect('accounts:admin_users')