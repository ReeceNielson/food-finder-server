from functools import wraps
from ..utils.supabase import supabase
from django.http import JsonResponse

def authenticate_required(view_func):
    """
    Decorator to authenticate requests using Supabase tokens.
    Extract the token from the Authorization header and validate it.
    
    Usage:
        @authenticate_required
        def my_view(request):
            return JsonResponse({'data': 'success'})
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        # Handle both "Bearer <token>" and just "<token>" formats
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header
        
        if not token:
            return JsonResponse(
                {'error': 'Missing authentication token'},
                status=401
            )
        
        try:
            # Validate token with Supabase
            supabase_response = supabase.auth.get_user(token)
            
            if supabase_response.user:
                # Attach user to request for use in the view
                request.user_id = supabase_response.user.id
                print("here")
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse(
                    {'error': 'Authentication failed'},
                    status=401
                )
        except Exception as e:
            return JsonResponse(
                {'error': f'Authentication error: {str(e)}'},
                status=401
            )
    
    return wrapper
