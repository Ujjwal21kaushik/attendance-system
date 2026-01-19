from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True)
    section = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.roll_no} - {self.name}"


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    teacher_id = models.CharField(max_length=20, unique=True)
    subject = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.teacher_id} - {self.name}"
