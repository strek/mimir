"""URL patterns for Phase views, scoped to playbook → workflow."""

from django.urls import path

from methodology import phase_views

urlpatterns = [
    path('', phase_views.phase_list, name='phase_list'),
    path('create/', phase_views.phase_create, name='phase_create'),
    path('<int:pk>/', phase_views.phase_detail, name='phase_detail'),
    path('<int:pk>/edit/', phase_views.phase_edit, name='phase_edit'),
    path('<int:pk>/delete/', phase_views.phase_delete, name='phase_delete'),
]
