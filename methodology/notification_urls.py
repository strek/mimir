"""URL configuration for notifications."""

from django.urls import path

from methodology import notification_views

app_name = "notifications"

urlpatterns = [
    path("", notification_views.notification_list, name="list"),
    path("<int:notification_id>/read/", notification_views.mark_read, name="mark_read"),
    path("read-all/", notification_views.mark_all_read, name="mark_all_read"),
]
