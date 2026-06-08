from django.db import models

class Stock(models.Model):
    """
    Master table of all stocks.
    
    Interview explanation:
    This is a reference table — every portfolio holding and alert references a Stock.
    We store symbol (NSE/BSE ticker), company name, sector, and exchange.
    """
    EXCHANGE_CHOICES = [
        ('NSE', 'National Stock Exchange'),
        ('BSE', 'Bombay Stock Exchange'),
        ('NASDAQ', 'NASDAQ'),
        ('NYSE', 'New York Stock Exchange'),
    ]

    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100, blank=True, null=True)
    exchange = models.CharField(max_length=10, choices=EXCHANGE_CHOICES, default='NSE')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

    class Meta:
        db_table = 'stocks'
        ordering = ['symbol']
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['sector']),
        ]
