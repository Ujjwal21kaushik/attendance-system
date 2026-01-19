from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import AttendanceSession, AttendanceRecord,Lecture,StudentLecture
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from face_auth.models import StudentFace
from django.contrib.auth.models import User
from location_auth.models import ClassroomLocation
from network_auth.models import NetworkSession
from network_auth.utils import get_client_ip

@login_required(login_url="/login/student/")
def mark_attendance(request, lecture_id):

    # 1️⃣ Only students allowed
    if not request.user.groups.filter(name="student").exists():
        return HttpResponseForbidden("Not allowed")

    # 2️⃣ Get lecture
    lecture = get_object_or_404(Lecture, id=lecture_id)
    today = timezone.localdate()

    # 3️⃣ Face registered?
    face_registered = StudentFace.objects.filter(
        student=request.user
    ).exists()

    # 4️⃣ TODAY’s active attendance session
    session = AttendanceSession.objects.filter(
        lecture=lecture,
        is_active=True,
        started_at__date=today
    ).first()

    if not session:
        return render(request, "attendance/mark_attendance.html", {
            "lecture": lecture,
            "face_registered": face_registered,
            "error": "Attendance is not active for today."
        })

    # 5️⃣ Already marked attendance TODAY?
    today_attendance = AttendanceRecord.objects.filter(
        student=request.user,
        lecture=lecture,
        date=today
    ).first()

    if today_attendance:
        return render(request, "attendance/mark_attendance.html", {
            "lecture": lecture,
            "face_registered": face_registered,
            "today_attendance": today_attendance,
            "success": "Attendance already marked for today."
        })


    location = ClassroomLocation.objects.filter(
        lecture=lecture
    ).first()

    radius = location.radius if location else None

    # 🔐 Session flags (set by AJAX checks)
    face_verified = request.session.get("face_verified", False)
    location_verified = request.session.get("location_verified", False)

    # 6️⃣ POST → Final submit
    if request.method == "POST":

        if not face_registered:
            return render(request, "attendance/mark_attendance.html", {
                "lecture": lecture,
                "face_registered": face_registered,
                "error": "Face registration required."
            })

        if not face_verified:
            return render(request, "attendance/mark_attendance.html", {
                "lecture": lecture,
                "face_registered": face_registered,
                "error": "Face verification required."
            })

        if not location_verified:
            return render(request, "attendance/mark_attendance.html", {
                "lecture": lecture,
                "face_registered": face_registered,
                "error": "Location verification required."
            })

        # ✅ Mark attendance
        AttendanceRecord.objects.create(
            student=request.user,
            lecture=lecture,
            date=today,
            status="present"
        )

        # 🔒 Clear verifications after success
        request.session.pop("face_verified", None)
        request.session.pop("location_verified", None)

        return render(request, "attendance/mark_attendance.html", {
            "lecture": lecture,
            "face_registered": face_registered,
            "today_attendance": True,
            "success": "Attendance marked successfully!"
        })

    # 7️⃣ GET → Fresh attendance page
    return render(request, "attendance/mark_attendance.html", {
        "lecture": lecture,
        "face_registered": face_registered,
        "radius": radius,
        "session_id": session.id   # 🔥 REQUIRED
    })


# --------------------------Start Attendance---------------------
@login_required(login_url='/login/teacher/')
@require_POST
def start_attendance(request):
    lecture_id = request.POST.get("lecture_id")

    session = AttendanceSession.objects.create(
        lecture_id=lecture_id,
        is_active=True,
        started_at=timezone.now()
    )

    # 🔥 NETWORK SESSION AUTO CREATE
    ip = get_client_ip(request)
    ip_prefix = ".".join(ip.split('.')[:3])

    NetworkSession.objects.create(
        session=session,
        ip_prefix=ip_prefix
    )

    return JsonResponse({
        "success": True,
        "session_id": session.id
    })



# --------------------------End Attendance---------------------
@login_required(login_url='/login/teacher/')
@require_POST
def end_attendance(request):
    if request.method != "POST":
        return JsonResponse({"success": False})

    lecture_id = request.POST.get("lecture_id")
    lecture = get_object_or_404(Lecture, id=lecture_id)
    today = timezone.localdate()

    session = AttendanceSession.objects.filter(
        lecture=lecture,
        is_active=True,
        started_at__date=today
    ).first()

    if not session:
        return JsonResponse({"success": False})

    # end session
    session.is_active = False
    session.ended_at = timezone.now()
    session.save()

    # AUTO ABSENT
    # 1️⃣ students assigned to lecture (USER ids)
    all_students = StudentLecture.objects.filter(
        lecture=lecture
    ).select_related("student__user").values_list(
        "student__user_id", flat=True
    )

    # 2️⃣ safety filter → ONLY students (no teachers, no junk)
    all_students = User.objects.filter(
        id__in=all_students,
        groups__name="student"
    ).values_list("id", flat=True)

    # 3️⃣ students who marked present today
    present_students = AttendanceRecord.objects.filter(
        lecture=lecture,
        date=today
    ).values_list("student_id", flat=True)

    # 4️⃣ absent = assigned − present
    absent_students = set(all_students) - set(present_students)

    AttendanceRecord.objects.bulk_create([
        AttendanceRecord(
            student_id=user_id,
            lecture=lecture,
            date=today,
            status="absent"
        )
        for user_id in absent_students
    ])

    return JsonResponse({"success": True})



# ----------------Reprot----------------
@login_required
def attendance_report(request):

    if not request.user.groups.filter(name="teacher").exists():
        return JsonResponse({"success": False})

    lecture_id = request.GET.get("lecture_id")
    date = request.GET.get("date")  # YYYY-MM-DD

    lecture = Lecture.objects.get(id=lecture_id)

    # all students mapped to lecture
    student_links = StudentLecture.objects.filter(
        lecture=lecture
    ).select_related("student", "student__user")

    # ONLY present records for selected date
    present_records = AttendanceRecord.objects.filter(
        lecture=lecture,
        marked_at__date=date,
        status="present"
    )

    present_ids = set(
        present_records.values_list("student_id", flat=True)
    )

    report = []

    for sl in student_links:
        student = sl.student

        if student.user.id in present_ids:
            rec = present_records.get(student=student.user)
            status = "present"
            local_time = timezone.localtime(rec.marked_at)
            time = local_time.strftime("%H:%M")
        else:
            status = "absent"
            time = "—"

        report.append({
            "student_id": student.roll_no,
            "name": student.name,
            "date": date,
            "time": time,
            "status": status
        })

    return JsonResponse({
        "success": True,
        "report": report
    })


