"""
Custom middleware for Oura app
"""

class DisableCSRFForAPI:
    """Disable CSRF checks for /api/* endpoints"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Exempt all /api/* paths from CSRF
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        return self.get_response(request)

