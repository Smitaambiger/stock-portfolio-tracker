from django.core.management.base import BaseCommand
from stocks.models import Stock

SAMPLE_STOCKS = [
    {'symbol': 'INFY', 'name': 'Infosys Limited', 'sector': 'Information Technology', 'exchange': 'NSE'},
    {'symbol': 'TCS', 'name': 'Tata Consultancy Services', 'sector': 'Information Technology', 'exchange': 'NSE'},
    {'symbol': 'RELIANCE', 'name': 'Reliance Industries Limited', 'sector': 'Energy', 'exchange': 'NSE'},
    {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Limited', 'sector': 'Banking', 'exchange': 'NSE'},
    {'symbol': 'WIPRO', 'name': 'Wipro Limited', 'sector': 'Information Technology', 'exchange': 'NSE'},
    {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Limited', 'sector': 'Banking', 'exchange': 'NSE'},
    {'symbol': 'TATAMOTORS', 'name': 'Tata Motors Limited', 'sector': 'Automobiles', 'exchange': 'NSE'},
    {'symbol': 'BAJFINANCE', 'name': 'Bajaj Finance Limited', 'sector': 'NBFC', 'exchange': 'NSE'},
    {'symbol': 'HCLTECH', 'name': 'HCL Technologies Limited', 'sector': 'Information Technology', 'exchange': 'NSE'},
    {'symbol': 'SBIN', 'name': 'State Bank of India', 'sector': 'Banking', 'exchange': 'NSE'},
]

class Command(BaseCommand):
    help = 'Seed database with sample stocks'

    def handle(self, *args, **options):
        created = 0
        for stock_data in SAMPLE_STOCKS:
            _, was_created = Stock.objects.get_or_create(symbol=stock_data['symbol'], defaults=stock_data)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} stocks. Total: {Stock.objects.count()}'))
