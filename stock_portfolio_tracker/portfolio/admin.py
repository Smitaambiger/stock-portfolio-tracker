from django.contrib import admin
from .models import PortfolioHolding, Transaction

@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'quantity', 'avg_buy_price', 'total_invested', 'updated_at']
    list_filter = ['stock__sector']
    search_fields = ['user__email', 'stock__symbol']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'transaction_type', 'quantity', 'price', 'transaction_date']
    list_filter = ['transaction_type']
