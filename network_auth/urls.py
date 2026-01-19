from django.urls import path
from . import views

urlpatterns = [
    path("create/<int:session_id>/", views.create_network_session),
    path("verify/<int:session_id>/", views.verify_network),
]
