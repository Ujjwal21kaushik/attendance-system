from django.urls import path
from .views import verify_face, register_face

urlpatterns = [
    path("verify/", verify_face, name="verify_face"),
    path("register/", register_face, name="register_face"),
]

 