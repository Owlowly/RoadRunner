from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from account.models import WishlistItem
from .models import Product, Type, Category,Review
from cart.forms import CartAddProductForm
from .recommender import Recommender
from .forms import ReviewForm, ContactForm


def product_list(request, type_slug=None, category_slug=None):
    type = None
    category = None
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    types = Type.objects.all()

    if type_slug:
        language = request.LANGUAGE_CODE
        type = get_object_or_404(Type,
                                 translations__language_code=language,
                                 translations__slug=type_slug)
        products = products.filter(type=type)

        if category_slug:
            language = request.LANGUAGE_CODE
            category = get_object_or_404(Category,
                                         translations__language_code=language,
                                         translations__slug=category_slug)
            products = products.filter(category=category)

    return render(
        request,
        'shop/product/list.html',
        {
            'category': category,
            'type': type,
            'categories': categories,
            'types': types,
            'products': products,
        }
    )

def product_detail(request, id, slug):
    language = request.LANGUAGE_CODE
    product = get_object_or_404(Product,
                                id=id,
                                translations__language_code=language,
                                translations__slug=slug,
                                available=True)
    avg_rating = Review.average_rating(product)

    cart_product_form = CartAddProductForm()
    in_wishlist = False
    r = Recommender()
    recommended_products = r.suggest_products_for([product], 3)
    if request.user.is_authenticated:
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()

    return render(request,
                  'shop/product/detail.html',
                  {'product': product,
                   'avg_rating': avg_rating,
                   'cart_product_form': cart_product_form,
                   'recommended_products': recommended_products,
                   'in_wishlist': in_wishlist})

@login_required
def review_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_review = Review.objects.filter(user=request.user, product=product).first()
    if user_review:
        return redirect('shop:review_edit', product_id=product_id, review_id=user_review.id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('shop:product_detail', id=product_id, slug=product.slug)
    else:
        form = ReviewForm()
    return render(request, 'shop/product/review_add.html', {'form': form})

@login_required
def review_edit(request, product_id, review_id):
    product = get_object_or_404(Product, id=product_id)
    review = get_object_or_404(Review, id=review_id)

    if request.user != review.user:
        return redirect('shop:product_detail', id=product_id, slug=product.slug)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('shop:product_detail', id=product_id, slug=product.slug)
    else:
        form = ReviewForm(instance=review)  # Pass the instance argument here

    return render(request, 'shop/product/review_edit.html', {'form': form, 'review': review})


@login_required
def review_delete(request, product_id, review_id):
    product = get_object_or_404(Product, id=product_id)
    review = get_object_or_404(Review, id=review_id, product=product)
    if request.user != review.user:
        return redirect('shop:product_detail', id=product_id, slug=product.slug)
    if request.method == 'POST':
        review.delete()
        return redirect('shop:product_detail', id=product_id, slug=product.slug)
    return HttpResponseNotAllowed(['POST'])


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = f"Sender's Email: {form.cleaned_data['email']}\n\n{form.cleaned_data['message']}"
            from_email = form.cleaned_data['email']
            recipient_list = ['djangochronics@gmail.com']
            send_mail(subject, message, from_email, recipient_list)
            return render(request, 'shop/contact_success.html')
    else:
        form = ContactForm()
    return render(request, 'shop/contact.html', {'form': form})


def success_view(request):
    return render(request, 'shop/contact_success.html')

