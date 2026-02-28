from django.shortcuts import render
from django.views import View
from django.http import JsonResponse


class HomeView(View):
    """Example view"""
    def get(self, request):
        return JsonResponse({'message': 'Welcome to Django!'})
