from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .utils.supabase import supabase
from .middleware.authentication import authenticate_required

class ProfileView(View):
    """Profile view"""
    @authenticate_required
    def get(self, request):
        return JsonResponse({'user_data': request.user_data})
    
    @authenticate_required
    def post(self, request):
        try:
            supabase_response = supabase.table('users').upsert(request.body).execute()
            return JsonResponse({'message': 'Profile updated successfully', 'data': supabase_response.data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class EventView(View):
    """Event view"""
    @authenticate_required
    def get(self, request):
        if request.method != 'GET':
            return JsonResponse({'error': 'Invalid request method'}, status=400)
        event_types = request.GET.get('event_types')
        try:
            query = supabase.from_('events').select('*')
            if event_types:
                query = query.filter('event_type', 'in', tuple(event_types.split(',')))
            events = query.execute()
            return JsonResponse({'events': events.data})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    @authenticate_required
    def post(self, request):
        try:
            supabase_response = supabase.table('events').insert(request.body).execute()
            return JsonResponse({'message': 'Event created successfully', 'data': supabase_response.data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class RunScheduledTasksView(View):
    """
    Endpoint triggered by Supabase Cron every 15 minutes to recalculate queue tiers.
    Protected by a secret token in the Authorization header.
    """
    def post(self, request):
        import os
        from .services.notification_queue import queue_manager
        
        cron_secret = os.getenv('CRON_SECRET')
        auth_header = request.headers.get('Authorization')
        
        # Verify the secure token is present and exactly matches what we expect
        # Supabase allows sending Bearer tokens or custom headers; we will look for:
        # Authorization: Bearer <token>
        expected_header = f"Bearer {cron_secret}"
        
        if not cron_secret or auth_header != expected_header:
            return JsonResponse({'error': 'Forbidden'}, status=403)
            
        try:
            queue_manager.recalculate_tiers()
            return JsonResponse({'message': 'Scheduled tasks executed successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
class RunScheduledTasksView(View):
    """
    Endpoint triggered by Supabase Cron every 15 minutes to recalculate queue tiers.
    Protected by a secret token in the Authorization header.
    """
    def post(self, request):
        import os
        from .services.notification_queue import queue_manager
        
        cron_secret = os.getenv('CRON_SECRET')
        auth_header = request.headers.get('Authorization')
        
        # Verify the secure token is present and exactly matches what we expect
        # Supabase allows sending Bearer tokens or custom headers; we will look for:
        # Authorization: Bearer <token>
        expected_header = f"Bearer {cron_secret}"
        
        if not cron_secret or auth_header != expected_header:
            return JsonResponse({'error': 'Forbidden'}, status=403)
            
        try:
            queue_manager.recalculate_tiers()
            return JsonResponse({'message': 'Scheduled tasks executed successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
