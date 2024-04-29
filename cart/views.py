from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product, Size
from .cart import Cart
from .forms import CartAddProductForm
from django.forms import forms
from coupons.forms import CouponApplyForm


def cart_detail(request):
    cart = Cart(request)
    for item_id, item_data in cart.cart.items():
        sizes_data = item_data.get('sizes', {})
        for size_name, size_info in sizes_data.items():
            size = size_name
            quantity = size_info['quantity']
        total_quantity = sum(size_info['quantity'] for size_info in sizes_data.values())
    coupon_apply_form = CouponApplyForm()
    return render(request, 'cart/detail.html', {'cart': cart, 'coupon_apply_form': coupon_apply_form})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST, product=product)

    if form.is_valid():
        cd = form.cleaned_data
        size = cd.get('size')
        quantity = cd['quantity']
        override_quantity = cd['override']
        cart.add(
            product=product,
            quantity=quantity,
            override_quantity=override_quantity,
            sizes=[size]
        )
    else:
        print(f'FORM ERROR: {form.errors}')
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id, size):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        cart.remove(product, size)
        return redirect('cart:cart_detail')
    except ValueError as e:
        return HttpResponseBadRequest(str(e))

