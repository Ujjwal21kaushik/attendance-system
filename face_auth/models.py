from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class StudentFace(models.Model):
    student = models.OneToOneField( 
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'student'}
    )
    encoding = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student.username



 