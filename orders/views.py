from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from cart.cart import Cart
from .forms import OrderCreateForm
from .models import Order, OrderItem


def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart:cart_detail')

    # Расчёт скидки
    discount_amount = Decimal('0')
    final_total = cart.get_total_price()

    if request.session.get('discount_applied'):
        discount_amount = final_total * Decimal('0.1')
        final_total = final_total - discount_amount

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'cash')
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            order.discount_amount = discount_amount

            if payment_method == 'online':
                # Сохраняем заказ ДО оплаты
                order.payment_method = 'online'
                order.is_paid = False
                order.status = 'pending'

                if request.user.is_authenticated:
                    order.user = request.user

                order.save()

                # Сохраняем товары
                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity']
                    )

                # Редирект на ЮMoney с ID заказа
                receiver = '4100119541837678'  # ЗАМЕНИ НА СВОЙ НОМЕР!
                success_url = request.build_absolute_uri(reverse('orders:payment_success', args=[order.id]))

                yoomoney_url = (
                    f'https://yoomoney.ru/quickpay/confirm.xml'
                    f'?receiver={receiver}'
                    f'&quickpay-form=shop'
                    f'&targets=Оплата заказа №{order.id} в ALPGEAR'
                    f'&sum={int(final_total)}'
                    f'&successURL={success_url}'
                )

                # Очищаем корзину, но не удаляем заказ
                cart.clear()

                return redirect(yoomoney_url)
            else:
                # Оплата при получении
                order.payment_method = 'cash'
                order.is_paid = False
                order.status = 'new'

                if request.user.is_authenticated:
                    order.user = request.user

                order.save()

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity']
                    )
                cart.clear()

                # Очищаем скидку из сессии
                if 'discount_applied' in request.session:
                    del request.session['discount_applied']

                messages.success(request, f'Заказ #{order.id} оформлен!')
                return redirect('orders:order_success', order_id=order.id)
        else:
            print(f"Ошибки формы: {form.errors}")
    else:
        form = OrderCreateForm()

    context = {
        'cart': cart,
        'form': form,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'has_discount': request.session.get('discount_applied', False)
    }
    return render(request, 'orders/create.html', context)


def payment_success(request, order_id):
    """Обработчик успешной оплаты через ЮMoney"""
    try:
        order = Order.objects.get(id=order_id)

        if not order.is_paid:
            order.is_paid = True
            order.paid_at = timezone.now()
            order.status = 'processing'
            order.save()

            # Помечаем промокод как использованный
            discount_code = request.session.get('discount_code_used')
            if discount_code:
                from shop.models import Subscriber
                try:
                    subscriber = Subscriber.objects.get(discount_code=discount_code)
                    subscriber.discount_used = True
                    subscriber.save()
                except:
                    pass

            # Очищаем скидку из сессии
            if 'discount_applied' in request.session:
                del request.session['discount_applied']
            if 'discount_code_used' in request.session:
                del request.session['discount_code_used']
            if 'discount_code' in request.session:
                del request.session['discount_code']

            messages.success(request, f'Заказ #{order.id} успешно оплачен!')
        else:
            messages.info(request, f'Заказ #{order.id} уже был оплачен')

        return redirect('orders:order_success', order_id=order.id)

    except Order.DoesNotExist:
        messages.error(request, 'Заказ не найден')
        return redirect('cart:cart_detail')


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/success.html', {'order': order})