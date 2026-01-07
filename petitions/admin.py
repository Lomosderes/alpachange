from django.contrib import admin
from .models import PromoContent, Category

@admin.register(PromoContent)
class PromoContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'is_active', 'created_at']
    list_filter = ['position', 'is_active']
    
admin.site.register(Category)