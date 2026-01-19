import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import StudentFace

from django.http import Http404
from .utils import (
    base64_to_image,
    get_face_encoding,
    serialize_encoding,
    deserialize_encoding, 
    verify_faces
)
@csrf_exempt
@login_required
def verify_face(request):

    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    image_base64 = data.get("image")
    lecture_id = data.get("lecture_id")

    if not image_base64:
        return JsonResponse({"success": False, "error": "No image received"}, status=400)

    image_path = base64_to_image(image_base64)
    live_encoding = get_face_encoding(image_path)

    if live_encoding is None:
        return JsonResponse({"success": False, "error": "Face not clear"})

    face_obj = StudentFace.objects.filter(student=request.user).first()

    if not face_obj:
        return JsonResponse({
            "success": False,
            "not_registered": True
        })

    stored_encoding = deserialize_encoding(face_obj.encoding)
    matched = verify_faces(stored_encoding, live_encoding)

    if matched:
        request.session["face_verified"] = lecture_id

    return JsonResponse({"success": bool(matched)})





@login_required
def register_face(request):

    # 🚫 If face already registered → block
    if StudentFace.objects.filter(student=request.user).exists():
        return redirect("attendance:mark_attendance", lecture_id=request.GET.get("lecture_id"))

    lecture_id = request.GET.get("lecture_id") or request.POST.get("lecture_id")
    
    if not lecture_id:
        raise Http404
    
    if request.method == "GET":
        return render(
            request,
            "face_auth/register_face.html",
            {"lecture_id": lecture_id}
        )

    if request.method == "POST":
        image = request.FILES.get("face_image")

        if not image:
            return render(
                request,
                "face_auth/register_face.html",
                {
                    "error": "Please upload an image",
                    "lecture_id": lecture_id
                }
            )

        encoding = get_face_encoding(image)

        if encoding is None:
            return render(
                request,
                "face_auth/register_face.html",
                {
                    "error": "Face not detected properly",
                    "lecture_id": lecture_id
                }
            )

        StudentFace.objects.create(
            student=request.user,
            encoding=serialize_encoding(encoding)
        )

        return redirect("attendance:mark_attendance", lecture_id=lecture_id)
