from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'last_name', 'address', 'city', 'postal_code']
    raw_id_fields = ['user']