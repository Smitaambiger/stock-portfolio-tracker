from rest_framework import serializers
from .models import PriceAlert
from stocks.models import Stock

class CreateAlertSerializer(serializers.Serializer):
    stock_symbol = serializers.CharField(max_length=20)
    condition = serializers.ChoiceField(choices=['ABOVE', 'BELOW'])
    target_price = serializers.DecimalField(max_digits=12, decimal_places=2)

class PriceAlertSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)

    class Meta:
        model = PriceAlert
        fields = ['id', 'stock_symbol', 'stock_name', 'condition', 'target_price',
                  'status', 'triggered_at', 'triggered_price', 'created_at']
