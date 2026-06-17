from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'comment', 'delivery_method'  # ← УБРАЛ payment_method
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Город, улица, дом, квартира', 'rows': 3}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Пожелания к заказу', 'rows': 2}),
            'delivery_method': forms.Select(attrs={'class': 'form-select'}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'payment_status', 'is_paid']  # ← добавить is_paid
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select rounded-0'}),
            'payment_status': forms.Select(attrs={'class': 'form-select rounded-0'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }