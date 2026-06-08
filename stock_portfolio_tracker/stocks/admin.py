from django.contrib import admin
from .models import Stock

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'sector', 'exchange', 'is_active']
    list_filter = ['exchange', 'sector', 'is_active']
    search_fields = ['symbol', 'name']
    list_editable = ['is_active']
