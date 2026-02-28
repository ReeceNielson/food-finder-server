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
