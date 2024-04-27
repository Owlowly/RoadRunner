import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import OrderItem, Order
from .forms import OrderCreateForm
from .tasks import order_created, payment_completed
from cart.cart import Cart
from shop.models import Size
import csv
import datetime
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from shop.recommender import Recommender


def clear_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']


def order_create(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                try:
                    size_instance = Size.objects.get(name=item['size'])

                except Size.DoesNotExist:
                    size_instance = None

                order_item = OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price'],
                )
                order_item.size.add(size_instance)
            r = Recommender()

            r.products_bought(cart)

            # clear the cart
            cart.clear()
            clear_coupon(request)
            cart.save()

            # launch asynchronous task, sending email order
            # order_created.delay(order.id)

            # sending PDF order
            # payment_completed.delay(order.id)

            return render(request,
                          'orders/order/created.html',
                          {'order': order, })
    else:
        if request.user.is_authenticated:
            user_info = request.user
            user_profile = request.user.profile
            form = OrderCreateForm(initial={
                'first_name': user_info.first_name,
                'last_name': user_info.last_name,
                'email': user_info.email,
                'address': user_profile.address,
                'postal_code': user_profile.postal_code,
                'city': user_profile.city
            })
        else:
            form = OrderCreateForm()

    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order/order_list.html', {'orders': orders})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})


@login_required
def export_to_csv(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    content_disposition = f'attachment; filename=order_{order_id}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)

    # Write the header row with all field names
    header_row = [
        'Id', 'User', 'First Name', 'Last Name', 'Email', 'Address', 'Postal Code',
        'City', 'Created', 'Paid', 'Item Name', 'Size', 'Quantity', 'Unit Price', 'Total Price'
    ]
    writer.writerow(header_row)

    # Write the data rows
    total_order_price = Decimal('0')
    for item in order.items.all():
        # Extract item details
        item_name = item.product.name
        size = ', '.join(size.name for size in item.size.all())
        quantity = item.quantity
        unit_price = item.product.price
        total_price = quantity * unit_price
        total_order_price += total_price
        # Construct the data row
        data_row = [
            order.id, order.user.id, order.first_name, order.last_name, order.email,
            order.address, order.postal_code, order.city, order.created, order.paid,
            item_name, size, quantity, unit_price, total_price
        ]
        writer.writerow(data_row)

    # Write the total order price as a separate row at the end
    writer.writerow(['Total Order Price', total_order_price])

    return response


"""
@login_required
def export_to_csv_2(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    content_disposition = f'attachment; filename=order_{order_id}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)

    # Get the fields of the Order object
    fields = order._meta.fields

    # Write a first row with header information
    writer.writerow([field.verbose_name.title() for field in fields])

    # Write data rows
    data_row = []
    for field in fields:
        value = getattr(order, field.attname)
        if isinstance(value, timezone.datetime):
            value = value.strftime('%d/%m/%Y')
        data_row.append(value)
    writer.writerow(data_row)

    return response
"""


@login_required
def order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(
        response,
        stylesheets=[
            weasyprint.CSS(os.path.join(settings.STATIC_ROOT, 'css', 'pdf.css'))
        ]
    )
    return response