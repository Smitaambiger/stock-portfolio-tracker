from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction
from decimal import Decimal
from .models import PortfolioHolding, Transaction
from .serializers import PortfolioHoldingSerializer, AddHoldingSerializer, TransactionSerializer
from stocks.models import Stock
from stocks.services import get_stock_price, get_multiple_prices


class PortfolioViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        GET /api/portfolio/
        Returns all holdings with live P&L calculation.
        Uses select_related to prevent N+1 query problem.
        Batch fetches all prices with caching.
        """
        holdings = PortfolioHolding.objects.filter(
            user=request.user
        ).select_related('stock')

        if not holdings.exists():
            return Response({
                'holdings': [],
                'summary': {'total_invested': 0, 'current_value': 0, 'total_pnl': 0, 'total_pnl_pct': 0}
            })

        symbols = [h.stock.symbol for h in holdings]
        prices = get_multiple_prices(symbols)

        holdings_data = []
        total_invested = Decimal('0')
        total_current_value = Decimal('0')

        for holding in holdings:
            price_info = prices.get(holding.stock.symbol, {})
            current_price = Decimal(str(price_info.get('price', 0)))
            current_value = current_price * holding.quantity
            pnl = current_value - holding.total_invested
            pnl_pct = (pnl / holding.total_invested * 100) if holding.total_invested > 0 else Decimal('0')

            total_invested += holding.total_invested
            total_current_value += current_value

            holdings_data.append({
                'id': holding.id,
                'stock': {
                    'symbol': holding.stock.symbol,
                    'name': holding.stock.name,
                    'sector': holding.stock.sector,
                },
                'quantity': float(holding.quantity),
                'avg_buy_price': float(holding.avg_buy_price),
                'total_invested': float(holding.total_invested),
                'current_price': float(current_price),
                'current_value': round(float(current_value), 2),
                'pnl': round(float(pnl), 2),
                'pnl_percentage': round(float(pnl_pct), 2),
            })

        total_pnl = total_current_value - total_invested
        total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else Decimal('0')

        return Response({
            'holdings': holdings_data,
            'summary': {
                'total_invested': round(float(total_invested), 2),
                'current_value': round(float(total_current_value), 2),
                'total_pnl': round(float(total_pnl), 2),
                'total_pnl_pct': round(float(total_pnl_pct), 2),
                'stocks_count': len(holdings_data),
            }
        })

    @action(detail=False, methods=['post'])
    def add(self, request):
        """POST /api/portfolio/add/ — Add stock to portfolio (atomic transaction)."""
        serializer = AddHoldingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        symbol = serializer.validated_data['stock_symbol'].upper()
        quantity = serializer.validated_data['quantity']
        buy_price = serializer.validated_data['buy_price']

        try:
            stock = Stock.objects.get(symbol=symbol, is_active=True)
        except Stock.DoesNotExist:
            return Response({'error': f'Stock {symbol} not found'}, status=status.HTTP_404_NOT_FOUND)

        with db_transaction.atomic():
            holding, created = PortfolioHolding.objects.get_or_create(
                user=request.user,
                stock=stock,
                defaults={
                    'quantity': quantity,
                    'avg_buy_price': buy_price,
                    'total_invested': quantity * buy_price,
                }
            )

            if not created:
                new_total_invested = holding.total_invested + (quantity * buy_price)
                new_quantity = holding.quantity + quantity
                holding.avg_buy_price = new_total_invested / new_quantity
                holding.quantity = new_quantity
                holding.total_invested = new_total_invested
                holding.save()

            Transaction.objects.create(
                user=request.user,
                stock=stock,
                transaction_type='BUY',
                quantity=quantity,
                price=buy_price,
                total_value=quantity * buy_price,
            )

        return Response({
            'message': f'{"Added" if created else "Updated"} {symbol} in portfolio',
            'holding': {
                'stock': symbol,
                'quantity': float(holding.quantity),
                'avg_buy_price': float(holding.avg_buy_price),
                'total_invested': float(holding.total_invested),
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def sell(self, request):
        """POST /api/portfolio/sell/ — Sell shares from portfolio."""
        symbol = request.data.get('stock_symbol', '').upper()
        quantity = Decimal(str(request.data.get('quantity', 0)))
        sell_price = Decimal(str(request.data.get('sell_price', 0)))

        try:
            stock = Stock.objects.get(symbol=symbol)
            holding = PortfolioHolding.objects.get(user=request.user, stock=stock)
        except (Stock.DoesNotExist, PortfolioHolding.DoesNotExist):
            return Response({'error': 'Holding not found'}, status=status.HTTP_404_NOT_FOUND)

        if quantity > holding.quantity:
            return Response({'error': f'You only have {holding.quantity} shares'}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            Transaction.objects.create(
                user=request.user, stock=stock, transaction_type='SELL',
                quantity=quantity, price=sell_price, total_value=quantity * sell_price,
            )
            if quantity == holding.quantity:
                holding.delete()
                return Response({'message': f'Sold all {symbol} shares', 'action': 'holding_removed'})
            else:
                holding.quantity -= quantity
                holding.total_invested = holding.avg_buy_price * holding.quantity
                holding.save()

        return Response({'message': f'Sold {quantity} shares of {symbol}', 'remaining': float(holding.quantity)})

    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """GET /api/portfolio/transactions/ — Full transaction history."""
        txns = Transaction.objects.filter(
            user=request.user
        ).select_related('stock').order_by('-transaction_date')[:50]
        serializer = TransactionSerializer(txns, many=True)
        return Response(serializer.data)
