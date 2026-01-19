from django.urls import path
from .views import set_location, get_location,verify_location

urlpatterns = [
    path("set/", set_location, name="set_location"),
    path("get/", get_location, name="get_location"),
    path("verify/", verify_location),
]
