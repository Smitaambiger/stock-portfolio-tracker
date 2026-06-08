from django.db import models
from django.conf import settings
from stocks.models import Stock

class PortfolioHolding(models.Model):
    """
    Represents one stock holding in a user's portfolio.
    
    Interview explanation:
    Each row = one stock a user owns.
    If user buys 50 INFY at 1800 and later buys 30 more at 1900,
    we update quantity and recalculate average buy price.
    
    P&L = (current_price - avg_buy_price) * quantity
    P&L % = (P&L / total_invested) * 100
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='holdings'
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='holdings'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    avg_buy_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_invested = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portfolio_holdings'
        unique_together = ['user', 'stock']  # One row per user per stock
        indexes = [models.Index(fields=['user', 'stock'])]

    def __str__(self):
        return f"{self.user.email} - {self.stock.symbol} ({self.quantity} shares)"


class Transaction(models.Model):
    """
    Records every buy/sell transaction.
    
    Interview explanation:
    PortfolioHolding stores CURRENT state.
    Transaction stores HISTORY — every buy and sell action.
    This is like a ledger.
    """
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date']
        indexes = [models.Index(fields=['user', 'transaction_date'])]

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.stock.symbol} @ {self.price}"
