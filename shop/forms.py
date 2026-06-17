from django import forms
from .models import Category, Product, Article
from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select rounded-0'}),
            'text': forms.Textarea(attrs={'class': 'form-control rounded-0', 'rows': 5, 'placeholder': 'Поделитесь впечатлениями о товаре...'}),
        }
        labels = {
            'rating': 'Ваша оценка',
            'text': 'Текст отзыва',
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'slug': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'image', 'description', 'price', 'available',
                  'brand', 'weight', 'material', 'difficulty_level']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select rounded-0'}),
            'name': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'slug': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'description': forms.Textarea(attrs={'class': 'form-control rounded-0', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control rounded-0'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'brand': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control rounded-0'}),
            'material': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'difficulty_level': forms.Select(attrs={'class': 'form-select rounded-0'}),
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'slug', 'excerpt', 'content', 'image', 'author', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'slug': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control rounded-0', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'form-control rounded-0', 'rows': 10}),
            'author': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }