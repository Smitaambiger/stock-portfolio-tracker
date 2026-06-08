from django.db import models
from django.conf import settings
from stocks.models import Stock

class PriceAlert(models.Model):
    """
    User-defined price alert.
    
    Interview explanation:
    User says: "Alert me when INFY crosses 2000."
    We store the condition. A Celery background task checks every 5 minutes
    whether the condition is met. If yes, we mark it triggered.
    
    This is why Redis + Celery is needed.
    Without background tasks, we'd have to check on every API request (bad).
    With Celery, we check on a schedule (efficient).
    """
    CONDITION_CHOICES = [
        ('ABOVE', 'Price goes above'),
        ('BELOW', 'Price goes below'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TRIGGERED', 'Triggered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alerts')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    target_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    triggered_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}: {self.stock.symbol} {self.condition} {self.target_price}"

    class Meta:
        db_table = 'price_alerts'
        indexes = [models.Index(fields=['status', 'stock'])]
