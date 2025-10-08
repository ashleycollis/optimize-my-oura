from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import OuraMetric, UserProfile, AIInsight
from .serializers import (
    OuraMetricSerializer,
    CoachSummaryResponseSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer
)
from .services.oura_service import OuraService
from .services.openai_service import OpenAIService
import logging  # might use this for better error tracking later

# from django.core.cache import cache  # TODO: use Redis instead of DB caching


class MetricsView(APIView):
    """
    Fetches Oura metrics with 1-hour cache to avoid hammering the API.
    TODO: Move caching logic to service layer
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, 404)
        
        if not profile.oura_access_token:
            return Response({'error': 'No Oura account connected'}, 400)
        
        # Check cache first (1 hour TTL)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_metrics = OuraMetric.objects.filter(
            user=request.user,
            updated_at__gte=one_hour_ago
        ).order_by('-date')[:7]
        
        if recent_metrics.count() == 7:
            serializer = OuraMetricSerializer(recent_metrics, many=True)
            return Response({'metrics': serializer.data})
        
        # Cache miss - fetch from Oura
        try:
            oura = OuraService(profile.oura_access_token)
            data = oura.fetch_metrics(days=7)
            # print(f"Fetched {len(data)} days from Oura")  # debug
            
            # Save to DB
            saved_metrics = []
            for item in data:
                # Could probably use bulk_create here but this works
                metric, _ = OuraMetric.objects.update_or_create(
                    user=request.user,
                    date=item['date'],
                    defaults={
                        'readiness_score': item.get('readiness_score'),
                        'sleep_score': item.get('sleep_score'),
                        'activity_score': item.get('activity_score'),
                        'sleep_duration': item.get('sleep_duration'),
                        'deep_sleep': item.get('deep_sleep'),
                        'rem_sleep': item.get('rem_sleep'),
                        'hrv': item.get('hrv'),
                        'resting_hr': item.get('resting_hr'),
                    }
                )
                saved_metrics.append(metric)
            
            serializer = OuraMetricSerializer(saved_metrics, many=True)
            return Response({'metrics': serializer.data})
            
        except Exception as e:
            # Log this somewhere eventually
            return Response({'error': f'Oura API error: {str(e)}'}, 500)


class CoachSummaryView(APIView):
    """Generate AI insights from recent metrics"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        metrics = OuraMetric.objects.filter(user=request.user).order_by('-date')[:7]
        
        if not metrics:
            return Response({'error': 'No metrics available'}, 400)
        
        metrics_data = OuraMetricSerializer(metrics, many=True).data
        
        # Check if we generated insights recently
        cached = AIInsight.objects.filter(
            user=request.user,
            insight_type='coach_summary',
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).first()
        
        if cached:
            # print(f"Cache hit for {request.user.username}")
            return Response({
                'explanation': cached.explanation,
                'suggestions': cached.suggestions
            })
        
        # Generate new insights
        ai = OpenAIService()
        result = ai.generate_coach_summary(metrics_data)
        
        # Save it
        AIInsight.objects.create(
            user=request.user,
            insight_type='coach_summary',
            explanation=result['explanation'],
            suggestions=result['suggestions']
        )
        
        return Response(result)


class TrendInsightView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        metrics = OuraMetric.objects.filter(user=request.user).order_by('-date')[:7]
        
        if not metrics:
            return Response({'error': 'No metrics'}, 400)
        
        data = OuraMetricSerializer(metrics, many=True).data
        
        # No caching here - trends change frequently enough
        ai = OpenAIService()
        result = ai.generate_trend_insight(data)
        return Response(result)


class ChatView(APIView):
    """
    AI chat about health data
    FIXME: Rate limit this to prevent abuse
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)
        
        msg = serializer.validated_data['message']
        
        # Get context from recent metrics
        metrics = OuraMetric.objects.filter(user=request.user).order_by('-date')[:7]
        metrics_data = OuraMetricSerializer(metrics, many=True).data
        
        try:
            ai = OpenAIService()
            result = ai.generate_chat_response(msg, metrics_data)
            return Response(result)
        except Exception as e:
            # TODO: Better error handling
            # print(f"Chat error: {str(e)}")
            return Response({'error': str(e)}, 500)


class ConnectOuraView(APIView):
    """
    Connect Oura via personal access token.
    Simpler than OAuth for MVP.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token required'}, 400)
        
        # Validate token by making a test call
        try:
            oura = OuraService(token)
            oura.fetch_metrics(days=1)  # Quick test
        except:
            return Response({'error': 'Invalid token'}, 400)
        
        # Save it
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.oura_access_token = token
        profile.token_created_at = timezone.now()
        profile.save()
        
        return Response({'message': 'Connected successfully'})
