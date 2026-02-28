from django.urls import path
from .views import ProfileView, EventView, RunScheduledTasksView

app_name = 'core'

urlpatterns = [
    path('events/', EventView.as_view(), name='events'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('api/cron/run-scheduled-tasks/', RunScheduledTasksView.as_view(), name='run-scheduled-tasks'),
]
