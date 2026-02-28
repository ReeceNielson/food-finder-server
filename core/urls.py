from django.urls import path
from .views import HomeView, Supabase


app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('supabase/', Supabase.get_events, name='supabase'),
]
