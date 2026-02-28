from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .utils.supabase import supabase

class HomeView(View):
    """Example view"""
    def get(self, request):
        return JsonResponse({'message': 'Welcome to Django!'})


class Supabase():
    @staticmethod
    def is_logged_in(self, request):
        # Example of checking if a user is logged in using Supabase
        try:
            response = supabase.auth.get_user()
            if response.user:
                return JsonResponse({'isLoggedIn': True, 'user': response.user})
            else:
                return JsonResponse({'isLoggedIn': False})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    @staticmethod
    def get_events(self, request):
        query = supabase.from_('events').select('*').execute()
        print(query)

        # if request.method != 'GET':
        #     return JsonResponse({'error': 'Invalid request method'}, status=400)
        # event_types = request.GET.get('event_types')
        # try:
        #     query = supabase.from_('events').select('*')
        #     if event_types:
        #         query = query.filter('event_type', 'in', tuple(event_types.split(',')))
        #     events = query.execute()
        #     return JsonResponse({'events': events.data})
        # except Exception as e:
        #     return JsonResponse({'error': str(e)})