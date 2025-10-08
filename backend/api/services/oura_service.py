import requests
from datetime import datetime, timedelta
from django.conf import settings
# import logging  # might need this later


class OuraService:
    """Handles Oura API calls"""
    
    def __init__(self, access_token):
        self.token = access_token
        self.base_url = settings.OURA_API_BASE
        self.headers = {'Authorization': f'Bearer {access_token}'}
    
    def fetch_metrics(self, days=7):
        """Fetch last N days of metrics"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # print(f"Fetching {days} days from {start_date} to {end_date}")
        
        try:
            sleep_data = self._fetch_endpoint('sleep', start_date, end_date)
            readiness_data = self._fetch_endpoint('daily_readiness', start_date, end_date)
            activity_data = self._fetch_endpoint('daily_activity', start_date, end_date)
            
            # Merge everything by date
            result = self._merge_data(sleep_data, readiness_data, activity_data)
            # print(f"Got {len(result)} days of data")
            return result
            
        except Exception as e:
            print(f"Error fetching Oura data: {e}")
            raise
    
    def _fetch_endpoint(self, endpoint, start_date, end_date):
        """Fetch from specific endpoint"""
        url = f"{self.base_url}/{endpoint}"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        
        # TODO: Add retry logic for rate limits
        response = requests.get(url, headers=self.headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def _merge_data(self, sleep_data, readiness_data, activity_data):
        """Merge different data sources by date"""
        data = {}
        
        # Start with sleep since it's usually most complete
        for item in sleep_data.get('data', []):
            date = item['day']
            # Convert seconds to hours (Oura returns seconds)
            data[date] = {
                'date': date,
                'sleep_score': item.get('score'),
                'sleep_duration': item.get('total_sleep_duration', 0) / 3600,
                'deep_sleep': item.get('deep_sleep_duration', 0) / 3600,
                'rem_sleep': item.get('rem_sleep_duration', 0) / 3600,
            }
        
        # Layer in readiness data
        for item in readiness_data.get('data', []):
            dt = item['day']
            if dt not in data:
                continue  # Skip if no sleep data for this day
            
            contribs = item.get('contributors', {})
            data[dt]['readiness_score'] = item.get('score')
            data[dt]['hrv'] = contribs.get('hrv_balance')
            data[dt]['resting_hr'] = contribs.get('resting_heart_rate')
        
        # Add activity scores
        for item in activity_data.get('data', []):
            dt = item['day']
            if dt in data:
                data[dt]['activity_score'] = item.get('score')
        
        # Sort by date
        return sorted(data.values(), key=lambda x: x['date'])

