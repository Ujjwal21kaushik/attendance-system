from django.urls import path , include
from accounts import views

urlpatterns = [
    path('student/', views.student_login, name='student_login'),
    path('teacher/', views.teacher_login, name='teacher_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path("logout/", views.logout_view, name="logout"),
 
]
 

 