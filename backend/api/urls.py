from django.urls import path
from .views import (
    MetricsView,
    CoachSummaryView,
    TrendInsightView,
    ChatView,
    ConnectOuraView,
)

urlpatterns = [
    # Oura data endpoints
    path('metrics/', MetricsView.as_view(), name='metrics'),
    path('connect-oura/', ConnectOuraView.as_view(), name='connect-oura'),
    
    # AI features
    path('coach-summary/', CoachSummaryView.as_view(), name='coach-summary'),
    path('trend-insight/', TrendInsightView.as_view(), name='trend-insight'),
    path('chat/', ChatView.as_view()),  # rate limiting needed
]
