from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    # Админ-панель
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/create/', views.admin_product_create, name='admin_product_create'),
    path('admin/products/edit/<int:product_id>/', views.admin_product_edit, name='admin_product_edit'),
    path('admin/products/delete/<int:product_id>/', views.admin_product_delete, name='admin_product_delete'),
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/categories/edit/<int:category_id>/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/categories/delete/<int:category_id>/', views.admin_category_delete, name='admin_category_delete'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/articles/', views.admin_articles, name='admin_articles'),
    path('admin/articles/create/', views.admin_article_create, name='admin_article_create'),
    path('admin/articles/edit/<int:article_id>/', views.admin_article_edit, name='admin_article_edit'),
    path('admin/articles/delete/<int:article_id>/', views.admin_article_delete, name='admin_article_delete'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/reset-password/<int:user_id>/', views.admin_user_reset_password,
         name='admin_user_reset_password'),
    path('admin/users/delete/<int:user_id>/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/users/delete/<int:user_id>/', views.admin_user_delete, name='admin_user_delete'),
]
