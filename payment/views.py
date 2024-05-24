from django.shortcuts import render, redirect, reverse, get_object_or_404
from decimal import Decimal
import stripe
from django.conf import settings

from orders.models import Order
from payment.tasks import payment_completed_task

# create the Stripe instance
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        # Stripe checkout session data
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        # Add order items to the Stripe checkout session
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * Decimal('100')),
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                },
                'quantity': item.quantity,
            })

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(**session_data)
        request.session['stripe_payment_intent'] = session.payment_intent
        return redirect(session.url, code=303)
    else:
        return render(request, 'payment/process.html', locals())


def payment_completed(request):
    # USe this part if Webhook not workin
    order_id = request.session.get('order_id', None)
    if order_id is None:
        return None
    order = get_object_or_404(Order, id=order_id)

    # Retrieve the Stripe payment intent ID from the session
    stripe_payment_intent = request.session.get('stripe_payment_intent')
    order.paid = True
    # order.stripe_id = stripe_payment_intent
    order.save()
    payment_completed_task(order.id)
    # print(f'Order_id: {order_id}, Order: {order}')
    return render(request, 'payment/completed.html', {'order': order})


def payment_canceled(request):
    return render(request, 'payment/canceled.html')