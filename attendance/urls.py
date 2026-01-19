from django.urls import path
from attendance import views

app_name = 'attendance'

urlpatterns = [
    path('mark/<int:lecture_id>/', views.mark_attendance, name='mark_attendance'),

    path("start/", views.start_attendance, name="start_attendance"),
    path("end/", views.end_attendance, name="end_attendance"),

    path("report/", views.attendance_report, name="attendance_report"),
]
