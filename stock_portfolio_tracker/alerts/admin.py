from django.contrib import admin
from .models import PriceAlert

@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'condition', 'target_price', 'status', 'triggered_at']
    list_filter = ['status', 'condition']
    search_fields = ['user__email', 'stock__symbol']
