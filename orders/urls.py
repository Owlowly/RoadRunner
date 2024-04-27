from django.urls import path
from . import views
from django.utils.translation import gettext_lazy as _

app_name = 'orders'

urlpatterns = [
    path(_('create/'), views.order_create, name='order_create'),
    path('order_list/', views.order_list, name='order_list'),
    path('order/<int:order_id>/export_to_csv/', views.export_to_csv, name='export_to_csv'),
    path('orders/<int:order_id>/order_pdf/', views.order_pdf, name='order_pdf'),
    path('admin/order/<int:order_id>/pdf/', views.order_pdf, name='order_pdf'),
    path('admin/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),

]