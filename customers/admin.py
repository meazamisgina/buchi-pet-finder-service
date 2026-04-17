from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # Only use fields that actually exist in your Customer model
    list_display = ('name', 'phone') 
    search_fields = ('name', 'phone')