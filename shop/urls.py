from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('contact/', views.contact_view, name='contact'),
    path('contact/success/', views.success_view, name='contact_success'),

    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('<int:product_id>/review_add', views.review_add, name='review_add'),
    path('<int:product_id>/review_edit/<int:review_id>/', views.review_edit, name='review_edit'),
    path('<slug:type_slug>/', views.product_list, name='product_list_by_type'),
    path('<slug:type_slug>/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:product_id>/review_delete/<int:review_id>/', views.review_delete, name='review_delete'),



]
