from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from shop.models import Product


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    created = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=30, blank=True, null=True )
    last_name = models.CharField(_('last_name'), max_length=50, blank=True, null=True)
    address = models.CharField(_('address'), max_length=250, blank=True, null=True)
    postal_code = models.CharField(_('postal_code'), max_length=20, blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.user}'


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'


