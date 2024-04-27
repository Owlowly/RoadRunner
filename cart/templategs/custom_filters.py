from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_cart_item(cart, product_id):
    return next((item for item in cart if item.product.id == product_id), None)
