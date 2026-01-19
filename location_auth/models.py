from django.db import models

# Create your models here.
from django.db import models
from attendance.models import Lecture

class ClassroomLocation(models.Model):
    lecture = models.OneToOneField(
        Lecture,
        on_delete=models.CASCADE,
        related_name="classroom_location"
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.PositiveIntegerField(help_text="meters")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lecture.subject} location"
