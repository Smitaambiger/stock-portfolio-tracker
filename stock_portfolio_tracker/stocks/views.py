from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Stock
from .serializers import StockSerializer, StockPriceSerializer
from .services import get_stock_price, get_multiple_prices

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/stocks/ — list all stocks
    GET /api/stocks/{id}/ — get stock detail
    GET /api/stocks/{id}/price/ — get live price (cached)
    GET /api/stocks/search/?q=TCS — search stocks
    """
    queryset = Stock.objects.filter(is_active=True)
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def price(self, request, pk=None):
        """Get live price for a single stock (with Redis caching)."""
        stock = self.get_object()
        price_data = get_stock_price(stock.symbol)
        
        if price_data:
            serializer = StockPriceSerializer(price_data)
            return Response(serializer.data)
        return Response({'error': 'Price not available'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search stocks by symbol or name."""
        query = request.query_params.get('q', '')
        if len(query) < 1:
            return Response({'error': 'Query must be at least 1 character'}, status=status.HTTP_400_BAD_REQUEST)
        
        stocks = Stock.objects.filter(
            is_active=True
        ).filter(
            symbol__icontains=query
        ) | Stock.objects.filter(
            is_active=True,
            name__icontains=query
        )
        serializer = StockSerializer(stocks[:10], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_sector(self, request):
        """Get stocks grouped by sector."""
        sector = request.query_params.get('sector', '')
        stocks = Stock.objects.filter(is_active=True)
        if sector:
            stocks = stocks.filter(sector__icontains=sector)
        serializer = StockSerializer(stocks, many=True)
        return Response({'count': stocks.count(), 'stocks': serializer.data})
