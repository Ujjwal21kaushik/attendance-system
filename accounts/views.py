from django.contrib.auth import authenticate, login , logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from attendance.models import AttendanceSession, AttendanceRecord,Lecture
# Create your views here
# --------------------student_login-----------------------------
def student_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.groups.filter(name="student").exists():
            login(request, user)
            return redirect("student_dashboard")

        return render(request, "auth/student_login.html", {
            "error": "Invalid student credentials"
        })

    return render(request, "auth/student_login.html")

# --------------------teacher_login-----------------------------
def teacher_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.groups.filter(name="teacher").exists():
            login(request, user)
            return redirect("teacher_dashboard")

        return render(request, "auth/teacher_login.html", {
            "error": "Invalid teacher credentials"
        })

    return render(request, "auth/teacher_login.html")

# --------------------student_dashboard-----------------------------
from attendance.models import (
    StudentLecture,
    AttendanceSession,
    AttendanceRecord
)

@login_required(login_url='/login/student/')
def student_dashboard(request):
    if not request.user.groups.filter(name="student").exists():
        return redirect("student_login")

    student = request.user.student
    today = timezone.localdate()

    student_lectures = StudentLecture.objects.filter(
        student=student,
        lecture__start_time__date=today
    ).select_related("lecture", "lecture__teacher")

    lecture_cards = []

    for sl in student_lectures:
        lecture = sl.lecture

        # attendance record for TODAY (if exists)
        attendance = AttendanceRecord.objects.filter(
            student=request.user,
            lecture=lecture,
            date=today
        ).first()

        # session active TODAY?
        session_active = AttendanceSession.objects.filter(
            lecture=lecture,
            is_active=True,
            started_at__date=today
        ).exists()

        # decide status
        if attendance:
            if attendance.status == "present":
                status = "present"
            else:
                status = "absent"
        else:
            status = "not_started"

        lecture_cards.append({
            "lecture": lecture,
            "status": status,
            "session_active": session_active
        })

    return render(request, "student_dashboard.html", {
        "lecture_cards": lecture_cards
    })


# --------------------teacher_dashboard-----------------------------
@login_required(login_url='/login/teacher/')
def teacher_dashboard(request):
    if not request.user.groups.filter(name="teacher").exists():
        return redirect("teacher_login")

    teacher = request.user.teacher

    lectures_qs = Lecture.objects.filter(teacher=teacher)

    lectures = []

    for lecture in lectures_qs:
        is_active = AttendanceSession.objects.filter(
            lecture=lecture,
            is_active=True
        ).exists()

        lectures.append({
            "id": lecture.id,
            "subject": lecture.subject,
            "is_active": is_active
        })

    return render(request, "teacher_dashboard.html", {
        "lectures": lectures
    })



# --------------------Logout-----------------------------
def logout_view(request):
    logout(request)
    return redirect("home")  # or redirect("student_login")


