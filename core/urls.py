from django.urls import path
from .views import ProfileView, EventView


app_name = 'core'

urlpatterns = [
    path('events/', EventView.as_view(), name='events'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
