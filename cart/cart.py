from decimal import Decimal
from django.conf import settings
from shop.models import Product, Size
from coupons.models import Coupon


class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            product_id = str(product.id)
            cart_item = cart[product_id]
            total_quantity = cart_item['quantity']
            total_price = Decimal('0')

            # Display each size as a separate product in the cart
            for size_name, size_data in cart_item['sizes'].items():
                quantity = size_data['quantity']
                price = Decimal(size_data['price'])
                total_price += price * quantity

                item = {
                    'product': product,
                    'quantity': quantity,
                    'size': size_name,
                    'price': str(price),
                    'total_price': str(price * quantity),
                }
                yield item

            self.cart[product_id]['quantity'] = total_quantity
            self.cart[product_id]['total_price'] = str(total_price)

        self.save()

    def __len__(self):
        total_items = 0
        for product_id, product_data in self.cart.items():
            sizes_data = product_data.get('sizes', {})
            total_items += sum(size_info['quantity'] for size_info in sizes_data.values())
        return total_items

    def add(self, product, quantity=1, override_quantity=False, sizes=None):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'sizes': {}, 'price': str(product.price)}

        if 'sizes' not in self.cart[product_id]:
            self.cart[product_id]['sizes'] = {}
        total_quantity = quantity

        for size in sizes:
            size_instance = Size.objects.get(product=product, name=size)
            existing_size = self.cart[product_id]['sizes'].get(size_instance.name)
            if existing_size:
                if override_quantity:
                    existing_size['quantity'] = quantity
                else:
                    existing_size['quantity'] += quantity
                total_quantity += existing_size['quantity']
            else:
                new_size = {
                    'id': size_instance.id,
                    'size': size_instance.name,
                    'quantity': quantity,
                    'price': str(product.price),
                }
                self.cart[product_id]['sizes'][size_instance.name] = new_size

        self.cart[product_id]['quantity'] = total_quantity
        self.cart[product_id]['price'] = str(product.price)
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product, size):
        product_id = str(product.id)
        if product_id in self.cart:
            size_instance = Size.objects.get(product=product, name=size)
            size_name = size_instance.name
            if size_name in self.cart[product_id]['sizes']:
                size_quantity = self.cart[product_id]['sizes'][size_name]['quantity']

                if size_quantity >= self.cart[product_id]['quantity']:
                    del self.cart[product_id]['sizes'][size_name]
                else:
                    self.cart[product_id]['quantity'] -= size_quantity
                    del self.cart[product_id]['sizes'][size_name]

                self.save()
            else:
                raise ValueError("Size not found for the specified product.")
        else:
            raise ValueError("Product not found in the cart.")


    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_total_price(self):
        total_price = Decimal('0')
        for product_id, product_data in self.cart.items():
            sizes_data = product_data.get('sizes', {})
            for size_info in sizes_data.values():
                price = Decimal(size_info['price'])
                quantity = size_info['quantity']
                total_price += price * quantity

        return total_price

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()


