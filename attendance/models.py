from django.db import models
from django.contrib.auth.models import User
from accounts.models import Teacher, Student
from django.utils import timezone
from django.utils.timezone import now

class Lecture(models.Model):
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="lectures"
    )
    room = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.subject} ({self.teacher.teacher_id})"


class AttendanceSession(models.Model):
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.lecture.subject} | Active={self.is_active}"




class AttendanceRecord(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'student'}
    )
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )
    date = models.DateField(default=now)
    status = models.CharField(
        max_length=10,
        choices=(('present', 'Present'), ('absent', 'Absent')),
        default='present'
    )
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lecture', 'date')

    def __str__(self):
        return f"{self.student.username} | {self.lecture.subject} | {self.date}"



    
class StudentLecture(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="student_lectures"
    )
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        related_name="lecture_students"
    )

    class Meta:
        unique_together = ("student", "lecture")

    def __str__(self):
        return f"{self.student.roll_no} -> {self.lecture.subject}"

