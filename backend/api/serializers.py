from rest_framework import serializers
from .models import OuraMetric


class OuraMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = OuraMetric
        fields = [
            'id', 'date', 'readiness_score', 'sleep_score', 'activity_score',
            'sleep_duration', 'deep_sleep', 'rem_sleep', 'bedtime_start',
            'hrv', 'resting_hr', 'steps', 'active_calories'
        ]


# Response serializers for OpenAI outputs
class CoachSummaryResponseSerializer(serializers.Serializer):
    explanation = serializers.CharField()
    suggestions = serializers.ListField(child=serializers.CharField())


class TrendInsightSerializer(serializers.Serializer):
    summary = serializers.CharField()
    takeaways = serializers.ListField(child=serializers.CharField())


# Chat serializers
class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500)

class ChatResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
