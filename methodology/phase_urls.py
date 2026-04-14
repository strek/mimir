"""URL patterns for Phase CRUD operations."""

from django.urls import path
from methodology import phase_views

urlpatterns = [
    # Phase list
    path('', phase_views.phase_list, name='phase_list'),
    
    # Phase create
    path('create/', phase_views.phase_create, name='phase_create'),
    
    # Phase detail
    path('<int:phase_pk>/', phase_views.phase_detail, name='phase_detail'),
    
    # Phase edit
    path('<int:phase_pk>/edit/', phase_views.phase_edit, name='phase_edit'),
    
    # Phase delete
    path('<int:phase_pk>/delete/', phase_views.phase_delete, name='phase_delete'),
]
