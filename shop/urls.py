from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('journal/', views.article_list, name='article_list'),
    path('journal/<slug:slug>/', views.article_detail, name='article_detail'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('compare/', views.compare_products, name='compare'),
    path('compare/add/<int:product_id>/', views.add_to_compare, name='add_to_compare'),
    path('compare/remove/<int:product_id>/', views.remove_from_compare, name='remove_from_compare'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<int:id>/<slug:slug>/add-review/', views.add_review, name='add_review'),
    path('my-reviews/', views.user_reviews, name='user_reviews'),
]
