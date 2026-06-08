from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'sector', 'exchange', 'is_active']

class StockPriceSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    price = serializers.FloatField()
    change = serializers.FloatField()
    change_pct = serializers.FloatField()
    volume = serializers.IntegerField()
    from_cache = serializers.BooleanField(default=False)
