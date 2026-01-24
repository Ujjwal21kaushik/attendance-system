from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from attendance.models import AttendanceSession
from .models import NetworkSession
from .utils import get_client_ip , get_network_prefix
import ipaddress
 
# -------------------- TEACHER --------------------
@login_required(login_url='/login/teacher/')
def create_network_session(request, session_id):

    session = AttendanceSession.objects.get(id=session_id)

    ip = get_client_ip(request)

    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.version == 4:
            prefix = ".".join(ip.split(".")[:3])
        else:
            prefix = ":".join(ip.split(":")[:3])
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid IP"})

    NetworkSession.objects.update_or_create(
        session=session,
        defaults={"ip_prefix": prefix}
    )

    return JsonResponse({
        "success": True,
        "network_prefix": prefix
    })



# -------------------- STUDENT --------------------
@login_required(login_url='/login/student/')
def verify_network(request, session_id):

    network = NetworkSession.objects.get(session_id=session_id)

    if not network.session.is_active:
        return JsonResponse({"allowed": False, "reason": "Session ended"})

    student_ip = get_client_ip(request)
    student_prefix = get_network_prefix(student_ip)
    print("student : "+ student_prefix)
    print("Teacher : "+ network.ip_prefix)
    if student_prefix == network.ip_prefix:
        return JsonResponse({"allowed": True})

    return JsonResponse({
        "allowed": False,
        "reason": "Different network"
    })
