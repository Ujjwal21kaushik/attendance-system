from django.contrib import admin
from .models import Lecture, StudentLecture, AttendanceSession, AttendanceRecord

# Register your models here.


admin.site.register(Lecture)
admin.site.register(StudentLecture)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)

 