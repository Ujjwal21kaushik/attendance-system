from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from attendance.models import AttendanceSession
from .models import NetworkSession
from .utils import get_client_ip


# -------------------- TEACHER --------------------
@login_required(login_url='/login/teacher/')
@login_required(login_url='/login/teacher/')
def create_network_session(request, session_id):
    try:
        session = AttendanceSession.objects.get(id=session_id)
    except AttendanceSession.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "AttendanceSession not found"
        }, status=404)

    ip = get_client_ip(request)
    ip_prefix = ".".join(ip.split('.')[:3])

    NetworkSession.objects.update_or_create(
        session=session,
        defaults={"ip_prefix": ip_prefix}
    )

    return JsonResponse({
        "success": True,
        "ip_prefix": ip_prefix
    })



# -------------------- STUDENT --------------------
@login_required(login_url='/login/student/')
def verify_network(request, session_id):
    student_ip = get_client_ip(request)

    try:
        network = NetworkSession.objects.select_related("session").get(
            session_id=session_id
        )
    except NetworkSession.DoesNotExist:
        return JsonResponse({
            "allowed": False,
            "reason": "Network session not found"
        })

    if not network.session.is_active:
        return JsonResponse({
            "allowed": False,
            "reason": "Attendance session ended"
        })

    if student_ip.startswith(network.ip_prefix):
        return JsonResponse({"allowed": True})

    return JsonResponse({
        "allowed": False,
        "student_ip": student_ip,
        "ip_prefix": network.ip_prefix
    })
