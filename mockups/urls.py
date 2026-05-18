from django.urls import path
from . import views

urlpatterns = [
    path("pips/", views.pip_list, name="mockup_pip_list"),
    path("pips/create/", views.pip_create, name="mockup_pip_create"),
    path("pips/<int:pip_id>/", views.pip_detail, name="mockup_pip_detail"),
    path("pips/<int:pip_id>/admin-review/", views.pip_admin_review, name="mockup_pip_admin_review"),
]
