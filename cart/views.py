from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from shop.models import Product, Subscriber
from .cart import Cart
from .forms import CartAddProductForm


def cart_detail(request):
    cart = Cart(request)
    final_total = cart.get_total_price()
    discount_amount = Decimal('0')

    if request.session.get('discount_applied'):
        discount_amount = final_total * Decimal('0.1')
        final_total = final_total - discount_amount

    for item in cart:
        # Максимальное количество = остаток на складе
        max_qty = item['product'].stock if item['product'].stock > 0 else 20
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'override': True},
            max_quantity=max_qty
        )

    context = {
        'cart': cart,
        'discount_amount': discount_amount,
        'final_total': final_total,
    }
    return render(request, 'cart/detail.html', context)


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        try:
            cart.add(
                product=product,
                quantity=cd['quantity'],
                override_quantity=cd['override']
            )
            messages.success(request, f'{product.name} добавлен в корзину')
        except ValueError as e:
            messages.error(request, str(e))

    next_url = request.POST.get('next', '/shop/')
    return redirect(next_url)


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f'{product.name} удалён из корзины')
    return redirect('cart:cart_detail')


@require_POST
def apply_discount(request):
    discount_code = request.POST.get('discount_code', '').upper().strip()

    if not discount_code:
        messages.error(request, 'Введите промокод')
        return redirect('cart:cart_detail')

    try:
        subscriber = Subscriber.objects.get(discount_code=discount_code, discount_used=False)
        request.session['discount_applied'] = True
        request.session['discount_code_used'] = discount_code
        messages.success(request, 'Промокод применён! Скидка 10%')
    except Subscriber.DoesNotExist:
        messages.error(request, 'Неверный промокод или он уже использован')

    return redirect('cart:cart_detail')


def remove_discount(request):
    if 'discount_applied' in request.session:
        del request.session['discount_applied']
        messages.info(request, 'Скидка отменена')
    return redirect('cart:cart_detail')