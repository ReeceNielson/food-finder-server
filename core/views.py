import json
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .utils.supabase import supabase
from .middleware.authentication import authenticate_required


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(View):
    """Profile view"""
    
    def options(self, request):
        """Handle CORS preflight requests"""
        return JsonResponse({})
    
    @method_decorator(authenticate_required)
    def get(self, request):
        try:
            user_data = supabase.table('users').select('*').eq('id', request.user_id).execute()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'user_data': user_data.data})
    
    @method_decorator(authenticate_required)
    def post(self, request):
        try:
            body = json.loads(request.body)
            body['id'] = request.user_id
            supabase_response = supabase.table('users').upsert(body).execute()
            return JsonResponse({'message': 'Profile updated successfully', 'data': supabase_response.data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EventView(View):
    """Event view"""
    
    def options(self, request):
        """Handle CORS preflight requests"""
        return JsonResponse({})
    
    @method_decorator(authenticate_required)
    def get(self, request):
        event_types = request.GET.get('event_types')
        try:
            query = supabase.from_('events').select('*')
            if event_types:
                types_list = [t.strip() for t in event_types.split(',')]
                or_conditions = ','.join([f'types.cs.["{t}"]' for t in types_list])
                query = query.or_(or_conditions)
            events = query.execute()
            return JsonResponse({'events': events.data})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    @method_decorator(authenticate_required)
    def post(self, request):
        try:
            body = json.loads(request.body)
            supabase_response = supabase.table('events').insert(body).execute()
            return JsonResponse({'message': 'Event created successfully', 'data': supabase_response.data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

