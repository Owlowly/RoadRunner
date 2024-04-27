from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'account'

urlpatterns = [

    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('delete_user/<int:user_id>/', views.delete_user, name='confirm_delete_user'),
    path('toggle_wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),

    path('', include('django.contrib.auth.urls')),

]