"""URL configuration for the Teams feature (Act 11).

Routes are intentionally flat — no playbook nesting —
because teams are first-class entities shared across playbooks.
"""

from django.urls import path

from methodology import team_views

app_name = "teams"

urlpatterns = [
    path("", team_views.teams_browse, name="teams_browse"),
    path("create/", team_views.teams_create, name="teams_create"),
    path("<int:pk>/", team_views.teams_detail, name="teams_detail"),
    path("<int:pk>/manage/", team_views.teams_manage, name="teams_manage"),
]
