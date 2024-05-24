from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import stripe
from django.conf import settings
from orders.models import Order
from .tasks import payment_completed_task
import json


@csrf_exempt
def stripe_webhook(request):
    # print('Webhook received')
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)

            order.paid = True
            # store Stripe payment ID
            order.stripe_id = session.payment_intent
            order.save()

            payment_completed_task(order.id)

    return HttpResponse(status=200)