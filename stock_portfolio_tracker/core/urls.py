from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Stock Portfolio Tracker API",
        default_version='v1',
        description="""
        Real-time Stock Portfolio Tracker Backend
        
        Features:
        - JWT Authentication
        - Portfolio Management (add/track stocks)
        - Live P&L Calculation with Redis caching
        - Price Alerts with background processing
        - Stock search and analytics
        
        Built with Django REST Framework, PostgreSQL/SQLite, Redis, Celery.
        """,
        contact=openapi.Contact(email="smitaambiger11@gmail.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Docs (Swagger UI)
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Auth
    path('api/auth/', include('users.urls')),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Core features
    path('api/stocks/', include('stocks.urls')),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/alerts/', include('alerts.urls')),
]
