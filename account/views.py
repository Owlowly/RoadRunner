from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext_lazy as _
from shop.models import Product
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, WishlistItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shop.views import product_list


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.username = user_form.cleaned_data['email']
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)

            return render(request, 'registration/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Login error')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Account updated successfully'))
            return redirect('shop:product_list')
        else:
            messages.error(request, _('Error updating your account'))
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile, initial={
            'address': request.user.profile.address,
            'postal_code': request.user.profile.postal_code,
            'city': request.user.profile.city
        })
    return render(request, 'registration/edit.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        return HttpResponse("You don't have permission for deleting")
    if request.method == 'POST':
        user.delete()
        return redirect('shop:product_list')
    else:
        return render(request, 'registration/confirm_delete_user.html', {'user': user})


@login_required
def wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'wishlist/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def wishlist_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item = WishlistItem.objects.filter(user=request.user, product=product)
    if item.exists():
        item.delete()

        return redirect('account:wishlist')
    else:

        return render(request, 'account/wishlist.html', {'product': product, 'item': None})



@login_required
def toggle_wishlist(request):
    product_id = request.POST.get('id')
    action = request.POST.get('action')

    if product_id and action:
        try:
            product = Product.objects.get(id=product_id)

            if action == 'add_to_wishlist':

                WishlistItem.objects.get_or_create(user=request.user, product=product)
                return JsonResponse({'success': True, 'message': 'Item added to wishlist'})

            elif action == 'remove_from_wishlist':

                WishlistItem.objects.filter(user=request.user, product=product).delete()
                return JsonResponse({'success': True, 'message': 'Item removed from wishlist'})

            else:
                return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

