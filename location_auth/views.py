from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ClassroomLocation
import math
# Create your views here.

@login_required
def set_location(request):
    if request.method != "POST":
        return JsonResponse({"success": False})

    lecture_id = request.POST.get("lecture_id")
    latitude = request.POST.get("latitude")
    longitude = request.POST.get("longitude")
    radius = request.POST.get("radius")

    ClassroomLocation.objects.update_or_create(
        lecture_id=lecture_id,
        defaults={
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius
        }
    )

    return JsonResponse({"success": True})


@login_required
def get_location(request):
    lecture_id = request.GET.get("lecture_id")

    try:
        location = ClassroomLocation.objects.get(lecture_id=lecture_id)
        return JsonResponse({
            "success": True,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "radius": location.radius
        })
    except ClassroomLocation.DoesNotExist:
        return JsonResponse({"success": False})




def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2 +
        math.cos(phi1) * math.cos(phi2) *
        math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@login_required
def verify_location(request):
    if request.method != "POST":
        return JsonResponse({"success": False})

    lecture_id = request.POST.get("lecture_id")
    student_lat = float(request.POST.get("latitude"))
    student_lng = float(request.POST.get("longitude"))

    try:
        location = ClassroomLocation.objects.get(lecture_id=lecture_id)
    except ClassroomLocation.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Classroom location not set"
        })

    distance = haversine(
        student_lat,
        student_lng,
        location.latitude,
        location.longitude
    )
    print("📍 Student Lat:", student_lat)
    print("📍 Student Lng:", student_lng)
    print("🏫 Teacher Lat:", location.latitude)
    print("🏫 Teacher Lng:", location.longitude)
    print("📏 Distance (meters):", round(distance, 2))

    if distance <= location.radius:
        request.session["location_verified"] = True
        return JsonResponse({
            "success": True,
            "distance": round(distance, 2)
        })

    return JsonResponse({
        "success": False,
        "distance": round(distance, 2)
    })

