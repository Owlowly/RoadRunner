from django import forms
from django.utils.translation import gettext_lazy as _
from shop.models import Product

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 11)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
        label=_('Quantity')
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )
    update_quantity = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super(CartAddProductForm, self).__init__(*args, **kwargs)

        if product:
            sizes = product.size.all()
            self.fields['size'] = forms.ModelChoiceField(
                queryset=sizes,
                empty_label=None,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
