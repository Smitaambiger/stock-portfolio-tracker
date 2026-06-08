from rest_framework import serializers
from .models import PortfolioHolding, Transaction
from stocks.serializers import StockSerializer

class TransactionSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'stock', 'stock_symbol', 'stock_name', 'transaction_type',
                  'quantity', 'price', 'total_value', 'notes', 'transaction_date']
        read_only_fields = ['id', 'total_value', 'transaction_date']

class AddHoldingSerializer(serializers.Serializer):
    """Serializer for adding a stock to portfolio."""
    stock_symbol = serializers.CharField(max_length=20)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    buy_price = serializers.DecimalField(max_digits=12, decimal_places=2)

class PortfolioHoldingSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    current_price = serializers.FloatField(read_only=True, default=0)
    current_value = serializers.FloatField(read_only=True, default=0)
    pnl = serializers.FloatField(read_only=True, default=0)
    pnl_percentage = serializers.FloatField(read_only=True, default=0)

    class Meta:
        model = PortfolioHolding
        fields = ['id', 'stock', 'quantity', 'avg_buy_price', 'total_invested',
                  'current_price', 'current_value', 'pnl', 'pnl_percentage', 'updated_at']
