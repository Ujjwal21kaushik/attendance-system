from django.db import models
from attendance.models import AttendanceSession
import ipaddress

class NetworkSession(models.Model):
    session = models.OneToOneField(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="network"
    )
    ip_prefix = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        try:
            ip_obj = ipaddress.ip_address(self.ip_prefix)

            if ip_obj.version == 4:
                self.ip_prefix = ".".join(self.ip_prefix.split(".")[:3])
            else:
                self.ip_prefix = ":".join(self.ip_prefix.split(":")[:3])

        except Exception:
            pass  # leave as-is if something weird happens

        # print("🔥 SAVING TO DB (FINAL):", self.ip_prefix)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session {self.session.id} - {self.ip_prefix}"