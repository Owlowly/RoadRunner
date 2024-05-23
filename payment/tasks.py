import os

from celery import shared_task
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from orders.models import Order
from io import BytesIO
from celery import shared_task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


@shared_task
# email for order, async task
def order_created(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully created.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        print(f"Order with id={order_id} does not exist.")
        return False

    subject = f'Order nr. {order.id}'
    message = f'Dear {order.first_name},\n\n' \
              f'You have successfully placed an order.' \
              f'Your order ID is {order.id}.'\
              f'Order Details:\n'

    for item in order.items.all():
        sizes = item.size.all()
        size_values = ', '.join([str(size) for size in sizes]) if sizes else "N/A"
        message += f'- {item.product.name}, Sizes: {size_values}, Quantity: {item.quantity}\n'

    message += f'\nTotal: ${order.get_total_cost()}'

    try:
        mail_sent = send_mail(subject, message, 'djangochronics@gmail.com', [order.email])
        print(f"Email sent successfully to {order.email}")
        return mail_sent
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


@shared_task
def payment_completed_task(order_id):
    """Task to send PDF when order complete. For sending PDF after successfully paid, use it in payment_app"""
    order = get_object_or_404(Order, id=order_id)
    # Create invoice email
    subject = f'RoadRunner - Invoice № {order.id}'
    message = 'Thank you for making this order. We are attached the invoice for your order'
    email = EmailMessage(subject, message, 'djangochronics@gmail.com', [order.email])

    # generate PDF
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(os.path.join(settings.STATIC_ROOT, 'css', 'pdf.css'))]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    # attach PDF file
    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    # send email
    email.send()