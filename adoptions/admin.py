from django.contrib import admin
from .models import Adoption

@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'pet_id', 'pet_source', 'requested_at')
    list_filter = ('pet_source', 'requested_at')
    search_fields = ('customer__name', 'customer__phone', 'pet_id')
    readonly_fields = ('requested_at',)