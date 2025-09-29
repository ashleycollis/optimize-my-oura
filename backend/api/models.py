from django.db import models
from django.contrib.auth.models import User


class OuraMetric(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField()
    
    #daily scores 
    readiness_score = models.IntegerField(null=True, blank=True)
    sleep_score = models.IntegerField(null=True, blank=True)
    activity_score = models.IntegerField(null=True, blank=True)
    
    # sleep data in hours 
    sleep_duration = models.FloatField(null=True, blank=True) 
    deep_sleep = models.FloatField(null=True, blank=True)
    rem_sleep = models.FloatField(null=True, blank=True)
    
    #physiological data 
    hrv = models.IntegerField(null=True, blank=True)
    resting_hr = models.IntegerField(null=True, blank=True)
    
    #OG payload returned from Oura API  
    raw_data = models.JSONField(default=dict, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    oura_access_token = models.CharField(max_length=500, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"


class AIInsight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insights')
    # type of AI feature - trend, chat, coach_summary
    insight_type = models.CharField(max_length=50)
    input_hash = models.CharField(max_length=64)
    
    #output from AI 
    explanation = models.TextField(blank=True)
    suggestions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'insight_type', 'input_hash']),
        ]
