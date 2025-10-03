from django.contrib import admin
from .models import OuraMetric, UserProfile, AIInsight


@admin.register(OuraMetric)
class OuraMetricAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'readiness_score', 'sleep_score', 
                    'activity_score', 'sleep_duration', 'hrv', 'resting_hr')
    list_filter = ('user', 'date')
    search_fields = ('user__username',)
    ordering = ('-date',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_created_at')
    search_fields = ('user__username',)
    readonly_fields = ('token_created_at',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('oura_access_token',)
        return self.readonly_fields


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ('user', 'insight_type', 'created_at')
    list_filter = ('user', 'insight_type', 'created_at')
    search_fields = ('user__username', 'insight_type')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
