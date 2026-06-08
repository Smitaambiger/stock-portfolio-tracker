from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal
from .models import PriceAlert
from .serializers import PriceAlertSerializer, CreateAlertSerializer
from stocks.models import Stock
from stocks.services import get_stock_price

class AlertViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/alerts/ — list all alerts for logged-in user."""
        status_filter = request.query_params.get('status', None)
        alerts = PriceAlert.objects.filter(user=request.user).select_related('stock')
        if status_filter:
            alerts = alerts.filter(status=status_filter.upper())
        serializer = PriceAlertSerializer(alerts, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        POST /api/alerts/
        Create a new price alert.
        """
        serializer = CreateAlertSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        symbol = serializer.validated_data['stock_symbol'].upper()
        try:
            stock = Stock.objects.get(symbol=symbol, is_active=True)
        except Stock.DoesNotExist:
            return Response({'error': f'Stock {symbol} not found'}, status=status.HTTP_404_NOT_FOUND)

        alert = PriceAlert.objects.create(
            user=request.user,
            stock=stock,
            condition=serializer.validated_data['condition'],
            target_price=serializer.validated_data['target_price'],
        )
        return Response(PriceAlertSerializer(alert).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        """DELETE /api/alerts/{id}/ — cancel an alert."""
        try:
            alert = PriceAlert.objects.get(pk=pk, user=request.user)
            alert.status = 'CANCELLED'
            alert.save()
            return Response({'message': 'Alert cancelled'})
        except PriceAlert.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def check_now(self, request):
        """
        POST /api/alerts/check_now/
        Manually trigger alert check (useful for demo/testing).
        In production, this runs automatically via Celery.
        """
        triggered = check_and_trigger_alerts(request.user)
        return Response({'message': f'{triggered} alert(s) checked/triggered'})

def check_and_trigger_alerts(user=None):
    """
    Check all active alerts and trigger matching ones.
    
    Interview explanation:
    This function is called by:
    1. Celery task every 5 minutes (background, automatic)
    2. Manual endpoint for demo/testing
    
    Logic:
    - For each active alert, get current stock price (from cache)
    - If condition met → mark as triggered
    """
    alerts = PriceAlert.objects.filter(status='ACTIVE').select_related('stock', 'user')
    if user:
        alerts = alerts.filter(user=user)

    triggered_count = 0
    for alert in alerts:
        price_data = get_stock_price(alert.stock.symbol)
        if not price_data:
            continue

        current_price = Decimal(str(price_data.get('price', 0)))
        condition_met = (
            (alert.condition == 'ABOVE' and current_price >= alert.target_price) or
            (alert.condition == 'BELOW' and current_price <= alert.target_price)
        )

        if condition_met:
            alert.status = 'TRIGGERED'
            alert.triggered_at = timezone.now()
            alert.triggered_price = current_price
            alert.save()
            triggered_count += 1

    return triggered_count
