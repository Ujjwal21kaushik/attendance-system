from django.db import models
from attendance.models import AttendanceSession

class NetworkSession(models.Model):
    session = models.OneToOneField(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="network"
    )
    ip_prefix = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session.id} - {self.ip_prefix}"
