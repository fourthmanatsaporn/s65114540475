
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Course,VideoCourse
from .models import CourseDetails
from django.http import HttpResponse
from .models import Banner
from .models import Staff
from .models import CourseOrder
from .models import VideoLesson  
from .models import UserProfile 
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import logout
from rest_framework.decorators import api_view , permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from .decorators import admin_required  , instructor_required  # นำเข้า Decorator
from django.contrib.auth.models import User, Group  # นำเข้า Group
from rest_framework.permissions import AllowAny, IsAdminUser
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from .models import InstructorProfile
from django.db.models import Q
from django.http import JsonResponse
import json
from django.core.files.storage import FileSystemStorage
from .models import CourseBooking
from django.db.models import Count
from django.core.paginator import Paginator
from .serializers import CourseDetailsSerializer, AddCourseSerializer ,BannerSerializer,VideoCourseOrderSerializer 
from myapp.serializers import CourseBookingSerializer
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random
import string
import datetime
from django.utils.timezone import now
import re
from .serializers import BookingDetailSerializer, CourseSerializer,BookingHistorySerializer,InstructorProfileSerializer
from django.contrib.auth import update_session_auth_hash
from django.core.files.base import ContentFile
import base64
from django.core.exceptions import ValidationError
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from django.contrib.auth.hashers import make_password
from myapp.models import InstructorProfile  # ✅ ตรวจสอบให้แน่ใจว่า import ถูกต้อง
# ✅ โค้ดใหม่ (ใช้ urllib.parse แทน)
from urllib.parse import quote 
from urllib.parse import quote
from django.db.models import Sum
from django.utils.timezone import now
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.offline as opy
from django.shortcuts import render
from django.db.models import Sum, Count
from datetime import datetime
from .models import CourseBooking, CourseOrder, Course,VideoCourseDetails,VideoCourseOrder
from datetime import timedelta  # ✅ Import timedelta แยกออกมา
from django.db.models.signals import post_save
from django.dispatch import receiver
#---------------------------------------------------------------------------------
import requests
from django.shortcuts import render
from django.http import HttpResponseForbidden
from .utils import grant_access_to_user  # ถ้า grant_access_to_user อยู่ในไฟล์ utils.py
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes

# ใส่ API Key ของคุณจาก Google Cloud
YOUTUBE_API_KEY = "AIzaSyBv1lfL1TwK2JyJqD_w1q1OwPtXWbZzal8"  # 🔴 เปลี่ยนเป็น API Key ของคุณ

def youtube_video_details(request):
    video_data = None  # ตัวแปรเก็บข้อมูลวิดีโอ
    error_message = None  # ตัวแปรเก็บข้อความผิดพลาด

    if request.method == "POST":
        video_id = request.POST.get("video_id")  # ดึงค่า Video ID จากฟอร์ม
        if video_id:
            url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={YOUTUBE_API_KEY}&part=snippet,statistics"
            response = requests.get(url)
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                video_data = data["items"][0]  # ดึงข้อมูลวิดีโอ
            else:
                error_message = "ไม่พบข้อมูลวิดีโอนี้ กรุณาตรวจสอบ Video ID อีกครั้ง"

    return render(request, "youtube_video.html", {"video_data": video_data, "error_message": error_message})

#------------------------------------------------FORviDeo--------------------------------

import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import VideoLesson
from .utils import upload_video_to_drive  # ฟังก์ชันอัปโหลดวิดีโอไป Google Drive
from decimal import Decimal  # ✅ ต้อง import ก่อนใช้


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_video_course_api(request):
    """
    API สำหรับเพิ่มคอร์สเรียนแบบวิดีโอ
    """
    title = request.data.get("title")
    description = request.data.get("description")
    price = request.data.get("price")
    instructor_name = request.data.get("instructor") 
    image = request.FILES.get("image")

    if not title or not description or not price or not image or not instructor_name:
        return Response({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

    course = VideoCourse.objects.create(
        title=title,
        description=description,
        price=price,
        image=image,
        instructor=instructor_name,
        added_by=request.user, 
        status="pending"
    )

    return Response({
        "message": "✅ คอร์สเรียนถูกสร้างแล้ว กรุณาเพิ่มรายละเอียดคอร์สต่อไป",
        "course_id": course.id,
        "next_step": reverse('add_video_course_details_api', kwargs={'course_id': course.id})
    }, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_video_course_details_api(request, course_id):
    """
    API สำหรับเพิ่มรายละเอียดของคอร์สเรียนแบบวิดีโอ
    """
    course = get_object_or_404(VideoCourse, id=course_id)

    name = request.data.get("name")
    description = request.data.get("description")
    additional_description = request.data.get("additional_description", "")
    image = request.FILES.get("image")
    additional_image = request.FILES.get("additional_image")
    preview_video = request.FILES.get("preview_video")

    if not name or not description or not image:
        return Response({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

    # ✅ บันทึกข้อมูลลงใน `VideoCourseDetails`
    VideoCourseDetails.objects.create(
        course=course,
        name=name,
        description=description,
        additional_description=additional_description,
        image=image,
        additional_image=additional_image,
        preview_video=preview_video
    )

    return Response({
        "message": "✅ รายละเอียดคอร์สถูกเพิ่มแล้ว กรุณาเพิ่มวิดีโอบทเรียน",
        "course_id": course.id,
        "next_step": reverse('add_video_lesson_api', kwargs={'course_id': course.id})
    }, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_video_lesson_api(request, course_id):
    """
    API สำหรับเพิ่มวิดีโอบทเรียนของคอร์สเรียน
    """
    course = get_object_or_404(VideoCourse, id=course_id)

    title = request.data.get("title")
    description = request.data.get("description")
    duration = request.data.get("duration")
    video_file = request.FILES.get("video_file")
    document = request.FILES.get("document")

    if not title or not description or not duration or not video_file:
        return Response({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

    # ✅ บันทึกไฟล์วิดีโอชั่วคราว
    temp_file_path = os.path.join("media", video_file.name)
    with open(temp_file_path, "wb+") as destination:
        for chunk in video_file.chunks():
            destination.write(chunk)
    destination.close()

    # ✅ อัปโหลดไป Google Drive
    google_drive_id = upload_video_to_drive(temp_file_path, video_file.name, request.user.email)

    # ✅ ลบไฟล์ชั่วคราว
    try:
        os.remove(temp_file_path)
    except PermissionError:
        print(f"❌ ไม่สามารถลบไฟล์: {temp_file_path}")

    # ✅ บันทึกวิดีโอเข้า DB
    VideoLesson.objects.create(
        course=course,
        title=title,
        description=description,
        google_drive_id=google_drive_id,
        duration=duration,
        instructor=request.user,
        document=document
    )

    return Response({
        "message": "✅ วิดีโอการสอนถูกเพิ่มแล้ว คอร์สเรียนจะถูกส่งไปให้แอดมินตรวจสอบ",
        "course_id": course.id,
        "status": "pending"
    }, status=201)

@login_required
def add_video_lesson(request, course_id):
    course = get_object_or_404(VideoCourse, id=course_id)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        duration = request.POST.get("duration")
        video_file = request.FILES.get("video_file")
        document = request.FILES.get("document")  

        if not title or not description or not duration or not video_file:
            return JsonResponse({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

        # บันทึกไฟล์วิดีโอชั่วคราว
        temp_file_path = os.path.join("media", video_file.name)
        with open(temp_file_path, "wb+") as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        destination.close()

        # อัปโหลดไป Google Drive
        google_drive_id = upload_video_to_drive(temp_file_path, video_file.name, request.user.email)

        # ลบไฟล์ชั่วคราว
        try:
            os.remove(temp_file_path)
        except PermissionError:
            print(f"❌ ไม่สามารถลบไฟล์: {temp_file_path}")

        # บันทึกวิดีโอเข้า DB
        VideoLesson.objects.create(
            course=course,
            title=title,
            description=description,
            google_drive_id=google_drive_id,
            duration=duration,
            instructor=request.user,
            document=document 
        )
        print("✅ อัปโหลดสำเร็จ กำลังเปลี่ยนเส้นทาง...")
        return redirect('instructor_live_courses')
  # ✅ ส่งกลับไปที่รายละเอียดคอร์ส

    return render(request, "instructor/add_video_lesson.html", {"course": course})


@login_required
def add_video_course(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        instructor_name = request.POST.get("instructor")  # ✅ รับค่าผู้สอนจากฟอร์ม
        image = request.FILES.get("image")

        if not title or not description or not price or not image or not instructor_name:
            return JsonResponse({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

        course = VideoCourse.objects.create(
            title=title,
            description=description,
            price=price,
            image=image,
            instructor=instructor_name,
            added_by=request.user,  # ✅ บันทึกเป็นชื่อผู้สอน
            status="pending"
        )

        return redirect(reverse('add_video_course_details', kwargs={'course_id': course.id}))
    
    return render(request, "instructor/add_video_course.html")



def video_courses(request):
    courses = VideoCourse.objects.filter(added_by=request.user)# ดึงข้อมูลคอร์สเรียนแบบวิดีโอทั้งหมด
    return render(request, "instructor/video_courses.html", {"courses": courses})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def video_courses_api(request):
    """
    API สำหรับดึงรายการคอร์สเรียนแบบวิดีโอ รวมถึงข้อความการแก้ไข
    """
    try:
        courses = VideoCourse.objects.all()

        course_data = [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "price": float(course.price),  # แปลง Decimal เป็น float
                "image_url": request.build_absolute_uri(course.image.url) if course.image else None,
                "instructor": course.instructor,
                "status": course.status,
                "revision_message": course.revision_message if course.revision_message else None,  # ✅ แสดงข้อความแก้ไข
                "created_at": course.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "payment_qr": request.build_absolute_uri(course.payment_qr.url) if course.payment_qr else None,
            }
            for course in courses
        ]

        return Response({"courses": course_data}, status=200)

    except Exception as e:
        return Response({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500)

@login_required
def video_course_details(request, course_id):
    course = get_object_or_404(VideoCourse, id=course_id)
    lessons = VideoLesson.objects.filter(course=course)

    return render(request, "instructor/video_course_details.html", {"course": course, "lessons": lessons})

@login_required
def add_video_course_details(request, course_id):
    course = get_object_or_404(VideoCourse, id=course_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        additional_description = request.POST.get('additional_description', '')
        image = request.FILES.get('image')
        additional_image = request.FILES.get('additional_image')
        preview_video = request.FILES.get('preview_video') 

        if not name or not description or not image:
            return JsonResponse({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

        # ✅ บันทึกข้อมูลลงใน `VideoCourseDetails`
        VideoCourseDetails.objects.create(
            course=course,
            name=name,
            description=description,
            additional_description=additional_description,
            image=image,
            additional_image=additional_image,
            preview_video=preview_video 
        )

        return redirect(reverse('add_video_lesson', kwargs={'course_id': course.id}))  


    return render(request, 'instructor/add_video_course_details.html', {"course": course})


def delete_selected_video_courses(request):
    if request.method == "POST":
        try:
            # ตรวจสอบการอ่านข้อมูลที่ถูกส่งมาจากฟอร์ม
            selected_courses = request.POST.getlist("selected_courses")  # รับค่า selected_courses
            if not selected_courses:
                messages.error(request, "กรุณาเลือกคอร์สที่ต้องการลบ")
                return redirect("instructor_live_courses")  # เปลี่ยนเส้นทางกลับไปที่หน้าคอร์ส

            # ลบคอร์สที่เลือก
            for course_id in selected_courses:
                course = get_object_or_404(VideoCourse, id=course_id)
                VideoCourseDetails.objects.filter(course=course).delete()  # ลบรายละเอียดคอร์ส
                VideoLesson.objects.filter(course=course).delete()  # ลบบทเรียนวิดีโอ
                course.delete()  # ลบคอร์สวิดีโอ

            messages.success(request, "ลบคอร์สเรียนสำเร็จ!")  # ส่งข้อความแจ้งเตือน
            return redirect("instructor_live_courses")  # เปลี่ยนเส้นทางกลับไปที่หน้าคอร์ส

        except json.JSONDecodeError:
            messages.error(request, "รูปแบบข้อมูลไม่ถูกต้อง")
            return redirect("instructor_live_courses")  # เปลี่ยนเส้นทางกลับไปที่หน้าคอร์ส

    messages.error(request, "ไม่สามารถลบคอร์สได้")
    return redirect("instructor_live_courses")  # เปลี่ยนเส้นทางกลับไปที่หน้าคอร์ส# เปลี่ยนเส้นทางกลับไปที่หน้าคอร์ส

#-----------------------------------------------api-------------------------------------
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])  # หรือเอาออกหากไม่ต้องการจำกัด
def delete_video_course_api(request, course_id):
    try:
        course = get_object_or_404(VideoCourse, id=course_id)

        # ลบข้อมูลที่เกี่ยวข้อง
        VideoCourseDetails.objects.filter(course=course).delete()
        VideoLesson.objects.filter(course=course).delete()
        course.delete()

        return Response({"message": "ลบคอร์สเรียนสำเร็จ!"}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": "เกิดข้อผิดพลาดในการลบคอร์ส: " + str(e)},
                        status=status.HTTP_400_BAD_REQUEST)
#-----------------------------------------------------------------------------------------------
@login_required
def edit_video_course(request, course_id):
    course = get_object_or_404(VideoCourse, id=course_id)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        image = request.FILES.get("image")

        if not title or not description or not price:
            return JsonResponse({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

        # อัปเดตรายละเอียดของคอร์ส
        course.title = title
        course.description = description
        course.price = price

        # อัปโหลดรูปภาพใหม่ (ถ้ามี)
        if image:
            if course.image:
                if os.path.exists(course.image.path):
                    os.remove(course.image.path)
            course.image = image
        course.status = 'revised'
        course.save()


        messages.success(request, "✅ คอร์สของคุณถูกส่งไปให้แอดมินตรวจสอบอีกครั้ง!")

        return redirect('edit_video_course_details', course_id=course.id)  # ✅ ไปยังหน้าถัดไป

    return render(request, "instructor/edit_video_course.html", {"course": course})

#-------------------------------------api---------------------------------------------

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_edit_video_course(request, course_id):
    course = get_object_or_404(VideoCourse, id=course_id, added_by=request.user)

    title = request.data.get("title")
    description = request.data.get("description")
    price = request.data.get("price")
    image = request.FILES.get("image")

    if not title or not description or not price:
        return Response({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

    course.title = title
    course.description = description
    course.price = price

    if image:
        if course.image and os.path.exists(course.image.path):
            os.remove(course.image.path)
        course.image = image

    course.status = 'revised'
    course.save()

    return Response({"message": "อัปเดตข้อมูลหลักของคอร์สสำเร็จ"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_course_api(request, course_id):
    course = get_object_or_404(VideoCourse, id=course_id, added_by=request.user)

    return Response({
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "price": course.price,
        "image_url": request.build_absolute_uri(course.image.url) if course.image else None,  # ✅
        "instructor": course.instructor,
        "status": course.status,
        "created_at": course.created_at,
    })

#----------------------------------------------------------------------------------------------------

@login_required
def edit_video_course_details(request, course_id):
    course_details = get_object_or_404(VideoCourseDetails, course_id=course_id)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        additional_description = request.POST.get("additional_description", "")
        image = request.FILES.get("image")
        additional_image = request.FILES.get("additional_image")
        preview_video = request.FILES.get("preview_video")

        if not name or not description:
            return JsonResponse({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

        # ✅ อัปเดตข้อมูลใน `VideoCourseDetails`
        course_details.name = name
        course_details.description = description
        course_details.additional_description = additional_description

        # ✅ จัดการอัปเดตรูปภาพ
        if image:
            if course_details.image and os.path.exists(course_details.image.path):
                os.remove(course_details.image.path)
            course_details.image = image
        
        if additional_image:
            if course_details.additional_image and os.path.exists(course_details.additional_image.path):
                os.remove(course_details.additional_image.path)
            course_details.additional_image = additional_image

        # ✅ จัดการอัปโหลดวิดีโอตัวอย่าง
        if preview_video:
            if course_details.preview_video and os.path.exists(course_details.preview_video.path):
                os.remove(course_details.preview_video.path)
            course_details.preview_video = preview_video

        course_details.course.status = 'revised'

        course_details.save()

        return redirect("edit_video_lesson", course_id=course_details.course.id)  # ✅ ไปยังหน้าถัดไป

    return render(request, "instructor/edit_video_course_details.html", {"course_details": course_details})

#-------------------------------------api---------------------------------------------

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_edit_video_course_details(request, course_id):
    details = get_object_or_404(VideoCourseDetails, course_id=course_id, )

    details.name = request.data.get("name", details.name)
    details.description = request.data.get("description", details.description)
    details.additional_description = request.data.get("additional_description", details.additional_description)

    if 'image' in request.FILES:
        if details.image and os.path.exists(details.image.path):
            os.remove(details.image.path)
        details.image = request.FILES['image']

    if 'additional_image' in request.FILES:
        if details.additional_image and os.path.exists(details.additional_image.path):
            os.remove(details.additional_image.path)
        details.additional_image = request.FILES['additional_image']

    if 'preview_video' in request.FILES:
        if details.preview_video and os.path.exists(details.preview_video.path):
            os.remove(details.preview_video.path)
        details.preview_video = request.FILES['preview_video']

    details.course.status = 'revised'
    details.save()

    return Response({"message": "อัปเดตรายละเอียดคอร์สสำเร็จ"})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_course_details_api(request, course_id):
    details = get_object_or_404(VideoCourseDetails, course_id=course_id, course__added_by=request.user)

    return Response({
        "id": details.id,
        "name": details.name,
        "description": details.description,
        "additional_description": details.additional_description,
        "image": details.image.url if details.image else None,
        "additional_image": details.additional_image.url if details.additional_image else None,
        "preview_video": details.preview_video.url if details.preview_video else None,
    })

#------------------------------------------------------------------------------------

@login_required
def edit_video_lesson(request, course_id):
    lesson = get_object_or_404(VideoLesson, course_id=course_id)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        duration = request.POST.get("duration")
        document = request.FILES.get("document")
        video_file = request.FILES.get("video_file")  # รับไฟล์วิดีโอใหม่

        if not title or not description or not duration:
            return JsonResponse({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

        # อัปเดตข้อมูลทั่วไป
        lesson.title = title
        lesson.description = description
        lesson.duration = duration

        # อัปเดตเอกสารแนบ
        if document:
            if lesson.document and os.path.exists(lesson.document.path):
                os.remove(lesson.document.path)  # ลบไฟล์เดิมถ้ามี
            lesson.document = document  # บันทึกไฟล์ใหม่

        # อัปโหลดวิดีโอใหม่ (ถ้ามี)
        if video_file:
            temp_file_path = os.path.join("media", video_file.name)
            with open(temp_file_path, "wb+") as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)

            # อัปโหลดไป Google Drive
            google_drive_id = upload_video_to_drive(temp_file_path, video_file.name)

            # ลบไฟล์วิดีโอเดิม (ถ้ามี)
            if lesson.google_drive_id:
                print(f"📌 ลบวิดีโอเก่า: {lesson.google_drive_id}")

            # อัปเดตข้อมูลไฟล์ใหม่
            lesson.google_drive_id = google_drive_id

            # ลบไฟล์ชั่วคราว
            try:
                os.remove(temp_file_path)
            except PermissionError:
                print(f"❌ ไม่สามารถลบไฟล์: {temp_file_path}")
        lesson.course.status = 'revised'
        lesson.save()
        print("✅ อัปเดตข้อมูลสำเร็จ กำลังเปลี่ยนเส้นทางไป video_courses...")
        return redirect("instructor_live_courses")  # ✅ กลับไปที่รายการคอร์สวิดีโอ

    return render(request, "instructor/edit_video_lesson.html", {"lesson": lesson})

#-------------------------------------api---------------------------------------------

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_edit_video_lesson(request, course_id):
    lesson = get_object_or_404(VideoLesson, course_id=course_id,instructor=request.user)

    lesson.title = request.data.get("title", lesson.title)
    lesson.description = request.data.get("description", lesson.description)
    lesson.duration = request.data.get("duration", lesson.duration)

    if 'document' in request.FILES:
        if lesson.document and os.path.exists(lesson.document.path):
            os.remove(lesson.document.path)
        lesson.document = request.FILES['document']

    if 'video_file' in request.FILES:
        video = request.FILES['video_file']
        temp_path = os.path.join("media", video.name)
        with open(temp_path, "wb+") as destination:
            for chunk in video.chunks():
                destination.write(chunk)

        # 👇 อัปโหลด Google Drive
        google_drive_id = upload_video_to_drive(temp_path, video.name)
        lesson.google_drive_id = google_drive_id

        os.remove(temp_path)

    lesson.course.status = 'revised'
    lesson.save()

    return Response({"message": "อัปเดตบทเรียนวิดีโอสำเร็จ"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_lesson_api(request, course_id):
    print(">>> User:", request.user)
    print(">>> Course ID:", course_id)

    # ✅ ตรวจสอบว่าผู้ใช้ซื้อคอร์สวิดีโอและได้รับการอนุมัติ
    # ✅ ตรวจสอบว่าผู้ใช้ซื้อคอร์สวิดีโอและได้รับการอนุมัติ
    order = VideoCourseOrder.objects.filter(
        user=request.user,
        course__id=course_id,
        payment_status='confirmed'
    ).first()

    if not order:
        return Response({'detail': 'คุณต้องซื้อคอร์สก่อน'}, status=403)

    # ✅ ดึงคอร์สและบทเรียนทั้งหมด
    course = get_object_or_404(VideoCourse, id=course_id)
    lessons = VideoLesson.objects.filter(course=course, status="approved")

    lesson_data = []
    for lesson in lessons:
        video_url = None
        if lesson.google_drive_id:
            # ✅ ให้สิทธิ์ผู้ใช้เข้าถึงวิดีโอบทเรียน
            grant_access_to_user(lesson.google_drive_id, request.user.email)

            # ✅ ใช้ URL สำหรับ WebView ที่แสดงผลได้ใน React Native
        video_url = f"https://drive.google.com/file/d/{lesson.google_drive_id}/preview"

        lesson_data.append({
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "duration": lesson.duration,
            "document": request.build_absolute_uri(lesson.document.url) if lesson.document else None,
            "video_url": video_url,
            "status": lesson.status,
        })

    return Response({
        "course": {
            "title": course.title,
            "description": course.description,
            "image": request.build_absolute_uri(course.image.url) if course.image else None,
        },
        "lessons": lesson_data
    })

#------------------------------------------------------------------------------------


def review_video_courses(request):
    """ ดึงคอร์สที่อยู่ในสถานะ 'รอการอนุมัติ' และ 'แก้ไขแล้วรอการตรวจสอบ' """
    courses = VideoCourse.objects.filter(status__in=['pending', 'revised'])
    return render(request, 'admin/review_video_courses.html', {'courses': courses})


def approve_video_course(request, course_id):
    """ อนุมัติคอร์สเรียนแบบวิดีโอ """
    course = get_object_or_404(VideoCourse, id=course_id)
    course.status = 'approved'
    course.save()

    # อัปเดต VideoLesson ที่เกี่ยวข้อง
    video_lessons = VideoLesson.objects.filter(course=course, status='pending')
    video_lessons.update(status='approved')  # อัปเดตสถานะให้เป็น approved

    messages.success(request, "✅ คอร์สเรียนได้รับการอนุมัติแล้วและ VideoLessons ที่เกี่ยวข้องได้รับการอนุมัติด้วย!")
    return redirect('review_video_courses')

@receiver(post_save, sender=VideoCourse)
def approve_video_lessons(sender, instance, created, **kwargs):
    """ เมื่อคอร์สเรียนแบบวิดีโอได้รับการอนุมัติ, อนุมัติ VideoLesson ด้วย """
    if instance.status == 'approved':
        # ดึง VideoLesson ที่เกี่ยวข้องกับ VideoCourse นี้
        video_lessons = VideoLesson.objects.filter(course=instance, status='pending')
        video_lessons.update(status='approved')  # อัปเดตสถานะให้เป็น approved

def send_back_video_course(request, course_id):
    """ ส่งคอร์สเรียนกลับไปแก้ไข """
    if request.method == 'POST':
        revision_message = request.POST.get('revision_message')
        course = get_object_or_404(VideoCourse, id=course_id)
        course.status = 'revision'
        course.revision_message = revision_message
        course.save()
        messages.warning(request, "⚠️ คอร์สถูกส่งกลับไปแก้ไขแล้ว!")
        return redirect('review_video_courses')

    return HttpResponseRedirect(reverse('review_video_courses'))

def upload_video_course_qr(request, course_id):
    """ ฟังก์ชันอัปโหลด QR Code สำหรับคอร์สเรียนแบบวิดีโอ """
    course = get_object_or_404(VideoCourse, id=course_id)

    if request.method == "POST" and 'payment_qr' in request.FILES:
        course.payment_qr = request.FILES['payment_qr']
        course.save()
        messages.success(request, "✅ อัปโหลด QR Code สำเร็จแล้ว!")
        return redirect('review_video_courses')

    messages.error(request, "⚠️ กรุณาอัปโหลดไฟล์ QR Code")
    return redirect('review_video_courses')
#-------------------------------------------------------------api-------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def review_video_courses_api(request):
    """ API ดึงคอร์สที่อยู่ในสถานะ 'รอการอนุมัติ' และ 'แก้ไขแล้วรอการตรวจสอบ' """
    courses = VideoCourse.objects.filter(status__in=['pending', 'revised'])
    course_data = [
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "instructor": course.instructor,
            "status": course.status,
            "revision_message": course.revision_message,
            "created_at": course.created_at,
            "image_url": request.build_absolute_uri(course.image.url) if course.image else None  # ✅ ดึงรูปภาพมาแบบเต็ม

        }
        for course in courses
    ]
    return Response({"courses": course_data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_video_course_api(request, course_id):
    """ API อนุมัติคอร์สเรียนแบบวิดีโอ """
    course = get_object_or_404(VideoCourse, id=course_id)
    course.status = 'approved'
    course.save()

    # อัปเดต VideoLesson ที่เกี่ยวข้อง
    VideoLesson.objects.filter(course=course, status='pending').update(status='approved')

    return Response({"message": "✅ คอร์สเรียนได้รับการอนุมัติและ VideoLessons ที่เกี่ยวข้องได้รับการอนุมัติด้วย!"})

@receiver(post_save, sender=VideoCourse)
def approve_video_lessons(sender, instance, created, **kwargs):
    """ เมื่อคอร์สเรียนได้รับการอนุมัติ, อนุมัติ VideoLesson ด้วย """
    if instance.status == 'approved':
        VideoLesson.objects.filter(course=instance, status='pending').update(status='approved')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_back_video_course_api(request, course_id):
    """ API ส่งคอร์สเรียนกลับไปแก้ไข """
    revision_message = request.data.get('revision_message', '')
    course = get_object_or_404(VideoCourse, id=course_id)
    course.status = 'revision'
    course.revision_message = revision_message
    course.save()
    return Response({"message": "⚠️ คอร์สถูกส่งกลับไปแก้ไขแล้ว!"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_video_course_qr_api(request, course_id):
    """ API อัปโหลด QR Code สำหรับคอร์สเรียนแบบวิดีโอ """
    course = get_object_or_404(VideoCourse, id=course_id)
    if 'payment_qr' in request.FILES:
        course.payment_qr = request.FILES['payment_qr']
        course.save()
        return Response({"message": "✅ อัปโหลด QR Code สำเร็จแล้ว!"})
    return Response({"error": "⚠️ กรุณาอัปโหลดไฟล์ QR Code"}, status=400)
#-------------------------------------------------------------------------------------------------------------------------

def video_course_details_user(request, course_id):
    """ แสดงรายละเอียดของคอร์สเรียนแบบวิดีโอ """
    course = get_object_or_404(VideoCourse, id=course_id)
    course_details = get_object_or_404(VideoCourseDetails, course_id=course_id)

    return render(request, 'video_course_details_user.html', {
        'course': course,
        'course_details': course_details
    })

@login_required
def purchase_video_course(request, course_id):
    course = get_object_or_404(VideoCourse, id=course_id)

    if request.method == "POST":
        payment_slip = request.FILES.get("payment_slip")
        if not payment_slip:
            messages.error(request, "⚠ กรุณาอัปโหลดสลิปการโอนเงิน")
            return redirect("purchase_video_course", course_id=course_id)

        # บันทึกข้อมูลคำสั่งซื้อ
        VideoCourseOrder.objects.create(
            user=request.user,
            course=course,
            payment_slip=payment_slip,
            payment_status="pending"  # รอแอดมินอนุมัติ
        )

        messages.success(request, "✅ คำสั่งซื้อของคุณถูกบันทึกแล้ว กรุณารอการตรวจสอบจากแอดมิน")
        return redirect("my_courses")  # ไปยังหน้าคอร์สของฉัน

    return render(request, "purchase_video_course.html", {"course": course})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def purchase_video_course_api(request, course_id):
    """
    API สำหรับซื้อคอร์สเรียนแบบวิดีโอ พร้อมแสดง QR Code สำหรับชำระเงิน
    """
    course = get_object_or_404(VideoCourse, id=course_id)

    # ✅ ดึง QR Code URL ทันทีเมื่อเข้า API
    qr_code_url = request.build_absolute_uri(course.payment_qr.url) if course.payment_qr else None

    if request.method == "GET":
        # ✅ ส่งข้อมูลคอร์ส + QR Code ไปแสดงก่อน
        return Response(
            {
                "course_id": course.id,
                "title": course.title,
                "description": course.description,
                "price": course.price,
                "image_url": request.build_absolute_uri(course.image.url) if course.image else None,
                "qr_code_url": qr_code_url,
            },
            status=status.HTTP_200_OK,
        )

    if request.method == "POST":
        # ตรวจสอบว่าผู้ใช้ซื้อคอร์สนี้ไปแล้วหรือยัง
        existing_order = VideoCourseOrder.objects.filter(user=request.user, course=course).first()
        if existing_order:
            return Response({"error": "คุณได้ซื้อคอร์สนี้ไปแล้ว"}, status=status.HTTP_400_BAD_REQUEST)

        # ตรวจสอบว่ามีสลิปการโอนเงินหรือไม่
        if "payment_slip" not in request.FILES:
            return Response({"error": "⚠ กรุณาอัปโหลดสลิปการโอนเงิน"}, status=status.HTTP_400_BAD_REQUEST)

        payment_slip = request.FILES["payment_slip"]

        # บันทึกไฟล์สลิปการโอนเงิน
        file_path = f"payment_slips/{payment_slip.name}"
        saved_path = default_storage.save(file_path, ContentFile(payment_slip.read()))

        # สร้างคำสั่งซื้อ
        order = VideoCourseOrder.objects.create(
            user=request.user,
            course=course,
            payment_slip=saved_path,  # เก็บ path ของสลิป
            payment_status="pending",  # รอแอดมินอนุมัติ
        )

        return Response(
            {
                "message": "✅ คำสั่งซื้อของคุณถูกบันทึกแล้ว กรุณารอการตรวจสอบจากแอดมิน",
                "order_id": order.id,
                "payment_slip_url": request.build_absolute_uri(default_storage.url(saved_path)),
                "qr_code_url": qr_code_url,  # ✅ ส่ง QR Code พร้อมกันเลย
            },
            status=status.HTTP_201_CREATED,
        )

def video_order_detail(request, order_id):
    """ แสดงรายละเอียดผู้ซื้อคอร์สเรียนแบบวิดีโอ """
    course = get_object_or_404(VideoCourse, id=order_id)
    orders = VideoCourseOrder.objects.filter(course=course)

    return render(request, "admin/video_order_detail.html", {
        "course": course,  # ✅ ส่งข้อมูลคอร์สวิดีโอไปยัง template
        "orders": orders,  # ✅ ส่งข้อมูลคำสั่งซื้อทั้งหมดไปยัง template
    })

def confirm_video_order(request, order_id):
    """ ✅ อนุมัติการชำระเงิน """
    order = get_object_or_404(VideoCourseOrder, id=order_id)
    order.payment_status = 'confirmed'
    order.save()
    messages.success(request, "✅ อนุมัติการชำระเงินเรียบร้อยแล้ว!")
    return redirect('video_order_detail', order.course.id)

def reject_video_order(request, order_id):
    """ ❌ ปฏิเสธการชำระเงิน """
    order = get_object_or_404(VideoCourseOrder, id=order_id)
    order.payment_status = 'rejected'
    order.save()
    messages.error(request, "❌ ปฏิเสธการชำระเงินแล้ว!")
    return redirect('video_order_detail', order.course.id)
#----------------------------------------------------api---------------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def video_order_detail_api(request, course_id):
    """
    API สำหรับดึงรายละเอียดผู้ซื้อคอร์สเรียนแบบวิดีโอ
    """
    course = get_object_or_404(VideoCourse, id=course_id)
    orders = VideoCourseOrder.objects.filter(course=course)

    # ✅ จัดรูปแบบข้อมูลให้ JSON
    orders_data = [
        {
            "order_id": order.id,
            "user": order.user.username,  # ✅ ชื่อผู้ซื้อ
            "email": order.user.email,  # ✅ อีเมลผู้ซื้อ
            "payment_status": order.payment_status,  # ✅ สถานะการชำระเงิน
            "payment_date": order.payment_date.strftime("%Y-%m-%d %H:%M:%S") if order.payment_date else None,
            "price": float(order.course.price) if order.course.price else 0.0,
            "course_title": order.course.title,
            "course_image": request.build_absolute_uri(order.course.image.url) if order.course.image else None,
            "payment_slip": request.build_absolute_uri(order.payment_slip.url) if order.payment_slip else None
        }
        for order in orders
    ]

    return Response({
        "course_id": course.id,
        "course_title": course.title,
        "course_image": request.build_absolute_uri(course.image.url) if course.image else None,
        "orders": orders_data,
        
    }, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_video_order_api(request, order_id):
    """
    ✅ API อนุมัติการชำระเงินคอร์สเรียนแบบวิดีโอ
    """
    order = get_object_or_404(VideoCourseOrder, id=order_id)
    order.payment_status = 'confirmed'
    order.save()
    
    return Response({
        "message": "✅ อนุมัติการชำระเงินเรียบร้อยแล้ว!",
        "order_id": order.id,
        "status": order.payment_status
    }, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_video_order_api(request, order_id):
    """
    ❌ API ปฏิเสธการชำระเงินคอร์สเรียนแบบวิดีโอ
    """
    order = get_object_or_404(VideoCourseOrder, id=order_id)
    order.payment_status = 'rejected'
    order.save()
    
    return Response({
        "message": "❌ ปฏิเสธการชำระเงินแล้ว!",
        "order_id": order.id,
        "status": order.payment_status
    }, status=200)

#----------------------------------------------------------------------------------------------------------------------------------------
@login_required
def video_lesson_view(request, course_id):
    # ดึงคอร์สเรียนแบบวิดีโอ
    course = get_object_or_404(VideoCourse, id=course_id)
    
    # ตรวจสอบว่าผู้ใช้ซื้อคอร์สนี้และได้รับการอนุมัติการชำระเงินแล้วหรือไม่
    order = VideoCourseOrder.objects.filter(user=request.user, course=course, payment_status='confirmed').first()
    
    if not order:
        return HttpResponseForbidden("คุณต้องทำการซื้อคอร์สนี้ก่อนถึงจะสามารถดูได้")

    # ดึงบทเรียนทั้งหมดที่เกี่ยวข้องกับคอร์สนี้
    lessons = VideoLesson.objects.filter(course=course)
    
    # ตรวจสอบสิทธิ์การเข้าถึงไฟล์ใน Google Drive (ถ้าไม่ได้รับอนุญาตจะทำการให้สิทธิ์)
    for lesson in lessons:
        if lesson.google_drive_id:  # ตรวจสอบว่าไฟล์มีอยู่ใน Google Drive
            grant_access_to_user(lesson.google_drive_id, request.user.email)
    
    return render(request, 'video_lesson_view.html', {
        'course': course,
        'lessons': lessons
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_video_lessons(request, course_id):
    """
    API สำหรับดึงข้อมูลวิดีโอการสอน และเอกสารประกอบการเรียน
    เฉพาะผู้ที่ซื้อคอร์สแล้วและได้รับการอนุมัติ
    """
    # ดึงคอร์สเรียน
    course = get_object_or_404(VideoCourse, id=course_id)

    # ตรวจสอบสิทธิ์การเข้าถึงคอร์ส
    order = VideoCourseOrder.objects.filter(user=request.user, course=course, payment_status='confirmed').first()
    if not order:
        return HttpResponseForbidden("คุณต้องทำการซื้อคอร์สนี้ก่อนถึงจะสามารถดูได้")

    # ดึงบทเรียนทั้งหมด
    lessons = VideoLesson.objects.filter(course=course, status="approved")

    lesson_data = []
    for lesson in lessons:
        video_url = None
        if lesson.google_drive_id:
            # ✅ ให้สิทธิ์ผู้ใช้ในการเข้าถึงไฟล์
            grant_access_to_user(lesson.google_drive_id, request.user.email)

            # ✅ ใช้ URL ที่เหมาะกับการเล่นใน React Native (WebView)
            video_url = f"https://drive.google.com/uc?id={lesson.google_drive_id}&export=download"

        lesson_data.append({
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "video_url": video_url,
            "duration": lesson.duration,
            "document": lesson.document.url if lesson.document else None,  
        })

    return JsonResponse({
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "image": course.image.url if course.image else None,
            "instructor": course.instructor,
        },
        "lessons": lesson_data
    })
@login_required
def video_order_detail_instructor(request, course_id):
    # ดึงคอร์สเรียนที่เลือก
    course = get_object_or_404(VideoCourse, id=course_id)
    
    # ดึงคำสั่งซื้อที่เกี่ยวข้องกับคอร์สนี้
    orders = VideoCourseOrder.objects.filter(course=course)
    
    return render(request, 'instructor/video_order_detail_instructor.html', {
        'course': course,
        'orders': orders,
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def video_order_detail_instructor_api(request, course_id):
    """
    API สำหรับดึงข้อมูลผู้ซื้อคอร์สเรียนแบบวิดีโอ สำหรับ Instructor
    """
    try:
        # ✅ ดึงคอร์สเรียนที่ Instructor ต้องการดู
        course = get_object_or_404(VideoCourse, id=course_id)

        # ✅ ดึงคำสั่งซื้อที่เกี่ยวข้องกับคอร์สนี้
        orders = VideoCourseOrder.objects.filter(course=course).select_related("user")

        # ✅ จัดรูปแบบข้อมูลก่อนส่งกลับ
        data = {
            "course_id": course.id,
            "course_title": course.title,
            "total_orders": orders.count(),
            "orders": [
                {
                    "order_id": order.id,
                    "buyer_name": order.user.get_full_name() if order.user.get_full_name() else order.user.username,
                    "email": order.user.email,
                    "payment_status": order.payment_status,
                    "payment_slip": request.build_absolute_uri(order.payment_slip.url) if order.payment_slip else None,
                    "transaction_id": order.transaction_id,
                    "payment_date": order.payment_date.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for order in orders
            ]
        }

        return Response(data, status=200)

    except Exception as e:
        return Response({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500)
#--------------------------------------------------------------------------------
def register(request):
    if request.method == 'POST':    
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        # ตรวจสอบความยาวของรหัสผ่าน
        if len(password) < 8:
            messages.error(request, 'รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร')
        elif password != password2:
            messages.error(request, 'รหัสผ่านไม่ตรงกัน')
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'ชื่อผู้ใช้นี้มีอยู่แล้ว')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'อีเมลนี้ถูกใช้ไปแล้ว')
            else:
                # สร้างผู้ใช้ใหม่
                user = User.objects.create(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=make_password(password)
                )
                user.save()


                try:
                    member_group = Group.objects.get(name='Member')  # ค้นหา Group ชื่อ 'Member'
                    user.groups.add(member_group)  # เพิ่มผู้ใช้เข้า Group
                except Group.DoesNotExist:
                    messages.warning(request, 'Group "Member" ยังไม่ได้ถูกสร้างในระบบ')

                messages.success(request, "สมัครสมาชิกสำเร็จ!")
                return redirect("register") 
            

    return render(request, 'register.html')



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)

            if user:
                # ✅ ตรวจสอบว่าผู้ใช้มีโปรไฟล์หรือไม่ ถ้าไม่มีให้สร้างใหม่
                profile, created = UserProfile.objects.get_or_create(user=user, defaults={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                })

                login(request, user)

                # ✅ ตรวจสอบว่าอยู่ในกลุ่มไหน และเปลี่ยนเส้นทางให้เหมาะสม
                if user.groups.filter(name='Instructor').exists():
                    return redirect('instructor_sales')
                elif user.groups.filter(name='Admin').exists():
                    return redirect('admin_dashboard')
                elif user.groups.filter(name='Member').exists():
                    return redirect('home')
                else:
                    messages.error(request, 'บทบาทของผู้ใช้งานไม่ถูกต้อง')
            else:
                messages.error(request, 'อีเมลหรือรหัสผ่านไม่ถูกต้อง')
        except User.DoesNotExist:
            messages.error(request, 'ไม่พบบัญชีผู้ใช้งานในระบบ')

    return render(request, 'login.html')

def staff_list_api(request):
    """
    API สำหรับดึงข้อมูลบุคลากรทั้งหมด
    """
    domain = request.build_absolute_uri('/').strip('/')
    staffs = Staff.objects.all()

    staff_data = [
        {
            "id": staff.id,
            "name": staff.name,
            "subject": staff.subject,
            "image_url": f"{domain}{staff.image.url}" if staff.image else None,
        }
        for staff in staffs
    ]

    return JsonResponse(staff_data, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # ✅ API ใช้ได้เฉพาะผู้ที่ล็อกอิน
def instructor_list_api(request):
    """
    API สำหรับดึงข้อมูลอาจารย์ทั้งหมด (เฉพาะที่ใช้ใน Mobile)
    """
    instructors = InstructorProfile.objects.select_related('user').all()
    
    instructor_data = [
        {
            "id": instructor.id,
            "full_name": f"{instructor.user.first_name} {instructor.user.last_name}",
            "age": instructor.age,
            "subject": instructor.subject,
            "profile_picture": request.build_absolute_uri(instructor.profile_picture.url) if instructor.profile_picture else None,
        }
        for instructor in instructors
    ]
    
    return JsonResponse(instructor_data, safe=False)



#-----------------------------------------------------------------สำหรับ API ------------------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------api สมาชิก --------------------------------------------------------

#ใช้เพื่อตรวจสอบ token ของฝั่ง mobile เเละดึงข้อมูลผู้ใช้งาน
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
    })



@api_view(['POST'])
@permission_classes([AllowAny])  # อนุญาตให้ทุกคนเข้าถึง API ได้
def register_api(request):
    """
    API สำหรับสมัครสมาชิก และเพิ่มเข้า Group ของ Django Admin
    """
    username = request.data.get('username')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    password = request.data.get('password')
    password2 = request.data.get('password2')

    if not username or not email or not password:
        return Response({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=status.HTTP_400_BAD_REQUEST)

    if password != password2:
        return Response({"error": "รหัสผ่านไม่ตรงกัน"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "ชื่อผู้ใช้นี้มีอยู่แล้ว"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"error": "อีเมลนี้ถูกใช้ไปแล้ว"}, status=status.HTTP_400_BAD_REQUEST)

    # สร้างบัญชีผู้ใช้
    user = User.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=make_password(password)
    )
    user.save()

    # เพิ่มผู้ใช้เข้า Group 'Member' โดยค่าเริ่มต้น
    try:
        member_group = Group.objects.get(name='Member')  # ค้นหา Group 'Member'
        user.groups.add(member_group)  # เพิ่มผู้ใช้เข้า Group
    except ObjectDoesNotExist:
        pass  # ถ้าไม่มี Group ก็ข้ามไป

    return Response({"message": "สร้างบัญชีสำเร็จแล้ว"}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])  # อนุญาตให้ทุกคนเข้าถึง API ได้
def login_api(request):
    """
    API สำหรับเข้าสู่ระบบและรับ JWT Token
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'กรุณากรอกอีเมลและรหัสผ่าน'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # ค้นหาผู้ใช้โดยใช้ email
        user = User.objects.get(email=email)
        user = authenticate(username=user.username, password=password)

        if user:
            # สร้าง JWT Token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # ตรวจสอบสิทธิ์จาก Django Groups
            user_group = "Member"  # ค่าเริ่มต้น

            if user.groups.filter(name='Instructor').exists():
                user_group = "Instructor"
            elif user.groups.filter(name='Admin').exists():
                user_group = "Admin"

            return Response({
                'access': access_token,
                'refresh': str(refresh),
                'group': user_group,
                'message': 'เข้าสู่ระบบสำเร็จ'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'อีเมลหรือรหัสผ่านไม่ถูกต้อง'}, status=status.HTTP_401_UNAUTHORIZED)

    except User.DoesNotExist:
        return Response({'error': 'ไม่พบผู้ใช้งานในระบบ'}, status=status.HTTP_404_NOT_FOUND)
    



@api_view(['GET'])
@permission_classes([AllowAny])
def get_video_course_details(request, course_id):
    """ API ดึงรายละเอียดของคอร์สเรียนแบบวิดีโอ """
    try:
        course = get_object_or_404(VideoCourse, id=course_id)
        course_details = get_object_or_404(VideoCourseDetails, course=course)

        data = {
            "id": course.id,
            "title": course.title,
            "price": course.price,
            "image_url": request.build_absolute_uri(course.image.url) if course.image else None,
            "instructor": course.instructor,
            "description": course_details.description,
            "additional_description": course_details.additional_description,
            "preview_video_url": request.build_absolute_uri(course_details.preview_video.url) if course_details.preview_video else None,
            "image_left_url": request.build_absolute_uri(course_details.image.url) if course_details.image else None,
            "image_right_url": request.build_absolute_uri(course_details.additional_image.url) if course_details.additional_image else None,
        }

        return Response(data, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_approved_courses(request):
    try:
        query = request.GET.get('q', '').strip()

        # ✅ ดึงแบนเนอร์ที่ได้รับอนุมัติ
        banners = Banner.objects.filter(status="approved").values("id", "image")

        # ✅ ดึงคอร์สที่ได้รับอนุมัติ
        approved_courses = Course.objects.filter(status='approved', is_closed=False).values(
            "id", "title", "price", "image", "instructor"
        )

        approved_video_courses = VideoCourse.objects.filter(status='approved').values(
            "id", "title", "price", "image", "instructor"
        )

        # ✅ ฟังก์ชันสร้าง URL รูปภาพให้ถูกต้อง
        def get_image_url(image_path):
            if image_path:
                return request.build_absolute_uri(f"{settings.MEDIA_URL}{image_path}")
            return None

        # ✅ แปลงข้อมูลคอร์สเป็น JSON
        courses_data = [
            {
                "id": course["id"],
                "title": course["title"],  
                "price": course["price"],
                "image_url": get_image_url(course["image"]),  # ✅ ใช้ฟังก์ชันแก้ไข URL
                "instructor": course["instructor"],
                "type": "คอร์สจอง"
            }
            for course in approved_courses
        ]

        video_courses_data = [
            {
                "id": course["id"],
                "title": course["title"],  
                "price": course["price"],
                "image_url": get_image_url(course["image"]),  # ✅ ใช้ฟังก์ชันแก้ไข URL
                "instructor": course["instructor"],
                "type": "คอร์สวิดีโอ"
            }
            for course in approved_video_courses
        ]

        banners_data = [
            {
                "id": banner["id"],
                "image_url": get_image_url(banner["image"]),  # ✅ แก้ URL
            }
            for banner in banners
        ]

        return Response({
            "banners": banners_data,
            "courses": courses_data,
            "video_courses": video_courses_data
        }, status=200)
    
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])  # อนุญาตให้ทุกคนเข้าถึง API นี้
def banners_api(request):
    """
    API สำหรับดึงรายการแบนเนอร์ทั้งหมด
    """
    try:
        banners = Banner.objects.all()
        banners_data = [
            {
                'id': banner.id,
                'image_url': request.build_absolute_uri(banner.image.url) if banner.image else None
            }
            for banner in banners
        ]
        return Response(banners_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
#---------------------------------------------api สมาชิก --------------------------------------------------------


#---------------------------------------------api ผู้สอน --------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def instructor_profile_api(request):
    """
    API สำหรับดึงข้อมูลโปรไฟล์ของ Instructor
    """
    user = request.user
    profile = user.profile
    data = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
        
    }
    return Response(data, status=status.HTTP_200_OK)

    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_instructor_profile_api(request):
    """
    API สำหรับอัปเดตข้อมูลโปรไฟล์ของ Instructor
    """
    user = request.user
    profile = user.profile

    user.username = request.data.get('username', user.username)
    user.first_name = request.data.get('first_name', user.first_name)
    user.last_name = request.data.get('last_name', user.last_name)
    user.email = request.data.get('email', user.email)
    
    if 'profile_picture' in request.FILES:
        if profile.profile_picture:
            profile.profile_picture.delete()  # ลบไฟล์รูปเก่าก่อนอัปโหลดใหม่
        profile.profile_picture = request.FILES['profile_picture']

    user.save()
    profile.save()

    return Response({"message": "อัปเดตโปรไฟล์สำเร็จ"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def instructor_sales_api(request):
    """
    API สำหรับดึงข้อมูลการขายของ Instructor ให้ตรงกับเว็บ
    """
    try:
        active_tab = request.GET.get("type", "booking")

        # ✅ คอร์สที่มีการจอง (รวมจำนวนการจอง)
        booked_courses = Course.objects.filter(
            id__in=CourseBooking.objects.values("course_id")
        ).annotate(booking_count=Count("coursebooking"))

        # ✅ หา CourseDetails ที่เกี่ยวข้อง
        course_details_dict = {cd.course_id: cd for cd in CourseDetails.objects.filter(course__in=booked_courses)}

        # ✅ คอร์สเรียนวิดีโอที่มีการซื้อ (รวมจำนวนการซื้อ)
        purchased_courses = VideoCourse.objects.filter(
            id__in=VideoCourseOrder.objects.values("course_id")
        ).annotate(purchase_count=Count("videocourseorder"))

        # ✅ จัดรูปแบบข้อมูลก่อนส่งกลับ
        data = {
            "active_tab": active_tab,
            "booked_courses": [
                {
                    "course_id": course.id,
                    "course_name": course.title if course.title else "N/A",
                    "booking_count": course.booking_count,
                    "course_image": request.build_absolute_uri(course.image.url)
                    if course.image and hasattr(course.image, "url")
                    else None,
                    "details": {
                        "course_title": course_details_dict[course.id].name if course.id in course_details_dict else "N/A",
                        "course_description": course_details_dict[course.id].description if course.id in course_details_dict else "N/A",
                        "course_price": float(course.price) if course.price else 0.0,
                    }
                }
                for course in booked_courses
            ],
            "purchased_courses": [
                {
                    "course_id": course.id,
                    "course_name": course.title if course.title else "N/A",
                    "purchase_count": course.purchase_count,
                    "course_image": request.build_absolute_uri(course.image.url)
                    if course.image and hasattr(course.image, "url")
                    else None,
                    "price": float(course.price) if course.price else 0.0,
                }
                for course in purchased_courses
            ]
        }

        return Response(data, status=200)

    except Exception as e:
        return Response({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def instructor_booking_detail_api(request, course_id):
    """
    API สำหรับดึงรายละเอียดการจองหลักสูตรของ Instructor
    """
    try:
        # ✅ ดึง Course จาก `course_id`
        course = get_object_or_404(Course, id=course_id)

        search_query = request.GET.get("search", "")

        # ✅ ดึงข้อมูลการจองจาก `CourseBooking`
        bookings = CourseBooking.objects.select_related("user").filter(course=course).order_by("-booking_date")

        if search_query:
            bookings = bookings.filter(student_name__icontains=search_query)  # ✅ ค้นหาจากชื่อผู้เรียน

        paginator = Paginator(bookings, 10)
        page_number = request.GET.get("page")
        bookings_page = paginator.get_page(page_number)

        # ✅ จัดรูปแบบข้อมูล
        data = {
            "course": {
                "id": course.id,
                "title": course.title,
            },
            "bookings": [
                {
                    "student_name_th": booking.student_name,
                    "student_name_en": booking.student_name_en,
                    "nickname_th": booking.nickname_th,
                    "nickname_en": booking.nickname_en,
                    "age": booking.age,
                    "grade": booking.grade,
                    "parent_nickname": booking.parent_nickname,
                    "phone": booking.phone,
                    "line_id": booking.line_id if booking.line_id else "ไม่มี",
                    "email": booking.user.email if booking.user else "ไม่มีข้อมูล",
                    "selected_course": booking.selected_course,
                    "payment_slip": request.build_absolute_uri(booking.payment_slip.url) if booking.payment_slip else None,
                    "booking_status": booking.get_booking_status_display(),
                    "booking_date": booking.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for booking in bookings_page
            ],
            "pagination": {
                "current_page": bookings_page.number,
                "total_pages": bookings_page.paginator.num_pages,
                "has_next": bookings_page.has_next(),
                "has_previous": bookings_page.has_previous(),
            }
        }

        return Response(data, status=200)

    except Exception as e:
        return Response({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500)
    
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_banner_api(request, banner_id):
    """✅ API สำหรับลบแบนเนอร์ของผู้สอน"""
    banner = get_object_or_404(Banner, id=banner_id, instructor=request.user)

    banner.delete()
    return Response({"message": "✅ ลบแบนเนอร์สำเร็จ!"}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_banner_api(request):
    """✅ API สำหรับเพิ่ม Banner ใหม่"""
    image = request.FILES.get("banner_image")
    if not image:
        return Response({"error": "กรุณาอัปโหลดรูปภาพ"}, status=status.HTTP_400_BAD_REQUEST)

    banner = Banner.objects.create(
        instructor=request.user,
        image=image,
        status="pending"
    )
    return Response({"message": "✅ เพิ่มเบนเนอร์สำเร็จ! โปรดรอการอนุมัติจากแอดมิน"}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_banners_api(request):
    """✅ API สำหรับดึง Banner ทั้งหมดของผู้สอนคนนั้น"""
    banners = Banner.objects.filter(instructor=request.user)
    serializer = BannerSerializer(banners, many=True, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_pending_banners_api(request):
    """✅ API สำหรับดึงเฉพาะ Banner ที่รอการอนุมัติ (Admin)"""
    banners = Banner.objects.filter(status="pending")
    serializer = BannerSerializer(banners, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def approve_banner_api(request, banner_id):
    """✅ API สำหรับอนุมัติ Banner (Admin)"""
    banner = get_object_or_404(Banner, id=banner_id)
    banner.status = "approved"
    banner.rejection_message = ""
    banner.save()
    return Response({"message": "✅ อนุมัติโฆษณาสำเร็จ!"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def reject_banner_api(request, banner_id):
    """✅ API สำหรับปฏิเสธ Banner (Admin)"""
    try:
        data = json.loads(request.body)
        rejection_message = data.get("rejection_message", "")

        banner = get_object_or_404(Banner, id=banner_id)
        banner.status = "rejected"
        banner.rejection_message = rejection_message
        banner.save()

        return Response({"message": "⛔ ปฏิเสธโฆษณาสำเร็จ!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_reservation_courses_api(request):
    """
    ✅ API ดึงข้อมูลคอร์สเรียนแบบจอง พร้อมแสดงข้อความที่แอดมินส่งกลับมา (revision_message)
    """
    try:
        courses = Course.objects.all()
        courses_data = []

        for course in courses:
            courses_data.append({
                'id': course.id,
                'title': course.title,
                'price': str(course.price),
                'instructor': course.instructor,
                'created_at': course.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status': course.status,
                'revision_message': course.revision_message if course.status == 'revision' else None,  # ✅ เพิ่มข้อความที่แอดมินส่งกลับมา
                'image_url': request.build_absolute_uri(course.image.url) if course.image else None,  # ✅ แสดง URL รูปภาพ
                'is_closed': course.is_closed,
            })

        return Response(courses_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_course_api(request):
    """
    ✅ API สำหรับเพิ่มคอร์สเรียน
    """
    try:
        title = request.data.get('title')
        description = request.data.get('description')
        instructor = request.data.get('instructor')
        price = request.data.get('price')
        image = request.FILES.get('image')

        # ตรวจสอบว่าข้อมูลครบถ้วน
        if not title or not description or not instructor or not price:
            return Response({"error": "กรุณากรอกข้อมูลให้ครบทุกช่อง"}, status=status.HTTP_400_BAD_REQUEST)

        course = Course.objects.create(
            title=title,
            description=description,
            instructor=instructor,
            price=price,
            image=image,
            added_by=request.user  # ✅ บันทึก ID ผู้ที่เพิ่มคอร์ส
        )
        return Response({"message": "✅ เพิ่มคอร์สเรียนสำเร็จ!", "course_id": course.id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_course_details_api(request, course_id):
    """
    ✅ API สำหรับเพิ่มรายละเอียดคอร์ส
    """
    try:
        course = get_object_or_404(Course, id=course_id)

        name = request.data.get('name')
        description = request.data.get('description')
        additional_description = request.data.get('additional_description')
        image = request.FILES.get('image')
        additional_image = request.FILES.get('additional_image')
        extra_image_1 = request.FILES.get('extra_image_1')
        extra_image_2 = request.FILES.get('extra_image_2')

        if not name or not description or not additional_description:
            return Response({"error": "กรุณากรอกข้อมูลให้ครบทุกช่อง"}, status=status.HTTP_400_BAD_REQUEST)

        course_details = CourseDetails.objects.create(
            course=course,
            name=name,
            description=description,
            additional_description=additional_description,
            image=image,
            additional_image=additional_image,
            extra_image_1=extra_image_1,
            extra_image_2=extra_image_2
        )
        return Response({"message": "✅ เพิ่มรายละเอียดคอร์สสำเร็จ!"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])  # ✅ เพิ่มบรรทัดนี้
@permission_classes([IsAuthenticated])
def edit_course_api(request, course_id):
    """
    ✅ API สำหรับแก้ไขคอร์สเรียนแบบจอง (ข้อมูลหลัก)
    """
    course = get_object_or_404(Course, id=course_id, added_by=request.user)

    title = request.data.get("title")
    description = request.data.get("description")
    instructor = request.data.get("instructor")
    price = request.data.get("price")
    image = request.FILES.get("image")

    if not title or not description or not price or not instructor:
        return Response({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

    course.title = title
    course.description = description
    course.instructor = instructor
    course.price = price

    if image:
        # ลบรูปเดิม (ถ้ามี)
        if course.image and os.path.exists(course.image.path):
            os.remove(course.image.path)
        course.image = image

    course.save()

    return Response({"message": "✅ แก้ไขคอร์สเรียนสำเร็จ!"}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_api(request, course_id):
    """
    ✅ API สำหรับดึงข้อมูลหลักของคอร์สเรียนแบบจอง
    """
    course = get_object_or_404(Course, id=course_id, added_by=request.user)

    return Response({
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "instructor": course.instructor,
        "price": course.price,
        "image_url": request.build_absolute_uri(course.image.url) if course.image else None,
        "created_at": course.created_at,
    })

@api_view(['PUT'])  
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def edit_course_details_api(request, course_id):
    """
    ✅ API สำหรับแก้ไขรายละเอียดคอร์สเรียนแบบจอง
    """
    course_details = get_object_or_404(CourseDetails, course__id=course_id)

    course_details.name = request.data.get('name', course_details.name)
    course_details.description = request.data.get('description', course_details.description)
    course_details.additional_description = request.data.get('additional_description', course_details.additional_description)

    if 'image' in request.FILES:
        course_details.image = request.FILES['image']
    if 'additional_image' in request.FILES:
        course_details.additional_image = request.FILES['additional_image']
    if 'extra_image_1' in request.FILES:
        course_details.extra_image_1 = request.FILES['extra_image_1']
    if 'extra_image_2' in request.FILES:
        course_details.extra_image_2 = request.FILES['extra_image_2']

    course_details.save()

    return Response({
        "message": "✅ แก้ไขรายละเอียดคอร์สสำเร็จ",
        "course_id": course_details.course.id
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_details_api(request, course_id):
    """
    ✅ API สำหรับดึงรายละเอียดคอร์สเรียนแบบจอง
    """
    course_details = get_object_or_404(CourseDetails, course__id=course_id, course__added_by=request.user)

    return Response({
        "name": course_details.name,
        "description": course_details.description,
        "additional_description": course_details.additional_description,
        "image": course_details.image.url if course_details.image else None,
        "additional_image": course_details.additional_image.url if course_details.additional_image else None,
        "extra_image_1": course_details.extra_image_1.url if course_details.extra_image_1 else None,
        "extra_image_2": course_details.extra_image_2.url if course_details.extra_image_2 else None,
    }, status=status.HTTP_200_OK)
 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_course_review_api(request, course_id):
    """✅ API สำหรับส่งคอร์สให้แอดมินตรวจสอบ"""
    try:
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        course.status = 'pending'  # ตั้งสถานะเป็นรออนุมัติ
        course.save()

        return Response({'message': '✅ ส่งคอร์สให้แอดมินตรวจสอบแล้ว!'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_course_api(request, course_id):
    """✅ API สำหรับลบคอร์สเดี่ยว (Mobile)"""
    course = get_object_or_404(Course, id=course_id,)
    print(f"📌 Added_by (ID ผู้เพิ่มคอร์ส): {course.added_by_id}")
    print(f"📌 User ID ที่ล็อกอิน: {request.user.id}")

    # ✅ ตรวจสอบสิทธิ์โดยใช้ ID
    if course.added_by_id != request.user.id:
        return Response({"error": "คุณไม่มีสิทธิ์ลบคอร์สนี้"}, status=status.HTTP_403_FORBIDDEN)

    # ลบคอร์ส
    course.delete()
    return Response({"message": "✅ ลบคอร์สสำเร็จ!"},status=status.HTTP_200_OK)  

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_course_api(request, course_id):
    """
    ✅ API สำหรับปิดการรับสมัครคอร์ส
    """
    try:
        course = get_object_or_404(Course, id=course_id)
        course.is_closed = True
        course.save()
        return Response({"message": "✅ สิ้นสุดการรับสมัครของคอร์สเรียบร้อยแล้ว"}, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({"error": "❌ ไม่พบคอร์สที่ต้องการปิดรับสมัคร"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reopen_course_api(request, course_id):
    """
    ✅ API สำหรับเปิดรับสมัครคอร์สอีกครั้ง
    """
    try:
        course = get_object_or_404(Course, id=course_id)
        course.is_closed = False
        course.save()
        return Response({"message": "✅ เปิดรับสมัครของคอร์สนี้อีกครั้งเรียบร้อยแล้ว"}, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({"error": "❌ ไม่พบคอร์สที่ต้องการเปิดรับสมัคร"}, status=status.HTTP_404_NOT_FOUND)




#---------------------------------------------api ผู้สอน --------------------------------------------------------


#---------------------------------------------api แอดมิน --------------------------------------------------------


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_admin_api(request):
    """
    API สำหรับดึงข้อมูลโปรไฟล์ของ Admin
    """
    user = request.user
    profile = user.profile
    data = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
        
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_admin_api(request):
    """
    API สำหรับอัปเดตข้อมูลโปรไฟล์ของ Admin
    """
    user = request.user
    profile = user.profile

    user.username = request.data.get('username', user.username)
    user.first_name = request.data.get('first_name', user.first_name)
    user.last_name = request.data.get('last_name', user.last_name)
    user.email = request.data.get('email', user.email)
    
    if 'profile_picture' in request.FILES:
        if profile.profile_picture:
            profile.profile_picture.delete()  # ลบไฟล์รูปเก่าก่อนอัปโหลดใหม่
        profile.profile_picture = request.FILES['profile_picture']

    user.save()
    profile.save()

    return Response({"message": "อัปเดตโปรไฟล์สำเร็จ"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sales_api(request):
    """
    API สำหรับดึงข้อมูลการขายของ Instructor ให้ตรงกับเว็บ
    """
    try:
        active_tab = request.GET.get("type", "booking")

        # ✅ คอร์สที่มีการจอง (รวมจำนวนการจอง)
        booked_courses = Course.objects.filter(
            id__in=CourseBooking.objects.values("course_id")
        ).annotate(booking_count=Count("coursebooking"))

        # ✅ หา CourseDetails ที่เกี่ยวข้อง
        course_details_dict = {cd.course_id: cd for cd in CourseDetails.objects.filter(course__in=booked_courses)}

        # ✅ คอร์สวิดีโอที่มีการซื้อ (รวมจำนวนการซื้อ)
        purchased_courses = VideoCourse.objects.filter(
            id__in=VideoCourseOrder.objects.values("course_id")  # ✅ ดึงเฉพาะคอร์สที่มีการซื้อ
        ).annotate(purchase_count=Count("videocourseorder"))  # ✅ นับจำนวนการซื้อคอร์สวิดีโอ

        # ✅ จัดรูปแบบข้อมูลก่อนส่งกลับ
        data = {
            "active_tab": active_tab,
            "booked_courses": [
                {
                    "course_id": course.id,
                    "course_name": course.title if course.title else "N/A",
                    "booking_count": course.booking_count,
                    "course_image": request.build_absolute_uri(course.image.url)
                    if course.image and hasattr(course.image, "url")
                    else None,  
                    "details": {
                        "course_title": course_details_dict[course.id].name if course.id in course_details_dict else "N/A",
                        "course_description": course_details_dict[course.id].description if course.id in course_details_dict else "N/A",
                        "course_price": float(course.price) if course.price else 0.0,
                    }
                }
                for course in booked_courses
            ],
            "purchased_courses": [
                {
                    "course_id": course.id,
                    "course_name": course.title if course.title else "N/A",
                    "purchase_count": course.purchase_count,
                    "course_image": request.build_absolute_uri(course.image.url)
                    if course.image and hasattr(course.image, "url")
                    else None,  
                    "details": {
                        "course_title": course.title,
                        "course_description": course.description if course.description else "N/A",
                        "course_price": float(course.price) if course.price else 0.0,
                    }
                }
                for course in purchased_courses
            ]
        }

        return Response(data, status=200)

    except Exception as e:
        return Response({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500)

   
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def Admin_booking_detail_api(request, course_id):
    """
    API สำหรับดึงรายละเอียดการจองหลักสูตรของ Instructor
    """
    try:
        # ✅ ดึง Course จาก `course_id`
        course = get_object_or_404(Course, id=course_id)

        search_query = request.GET.get("search", "")

        # ✅ ดึงข้อมูลการจองจาก `CourseBooking`
        bookings = CourseBooking.objects.select_related("user").filter(course=course).order_by("-booking_date")

        if search_query:
            bookings = bookings.filter(student_name__icontains=search_query)  # ✅ ค้นหาจากชื่อผู้เรียน

        paginator = Paginator(bookings, 10)
        page_number = request.GET.get("page")
        bookings_page = paginator.get_page(page_number)

        # ✅ จัดรูปแบบข้อมูล
        data = {
            "course": {
                "id": course.id,
                "title": course.title,
            },
            "bookings": [
                {
                    "id": booking.id,
                    "student_name_th": booking.student_name,
                    "student_name_en": booking.student_name_en,
                    "nickname_th": booking.nickname_th,
                    "nickname_en": booking.nickname_en,
                    "age": booking.age,
                    "grade": booking.grade,
                    "parent_nickname": booking.parent_nickname,
                    "phone": booking.phone,
                    "line_id": booking.line_id if booking.line_id else "ไม่มี",
                    "email": booking.user.email if booking.user else "ไม่มีข้อมูล",
                    "selected_course": booking.selected_course,
                    "payment_slip": request.build_absolute_uri(booking.payment_slip.url) if booking.payment_slip else None,
                    "booking_status": booking.get_booking_status_display(),
                    "booking_date": booking.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for booking in bookings_page
            ],
            "pagination": {
                "current_page": bookings_page.number,
                "total_pages": bookings_page.paginator.num_pages,
                "has_next": bookings_page.has_next(),
                "has_previous": bookings_page.has_previous(),
            }
        }

        return Response(data, status=200)

    except Exception as e:
        return Response({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_list_api(request):
    """
    ✅ API สำหรับดึงข้อมูลสมาชิกและผู้สอน
    """
    domain = request.build_absolute_uri('/')[:-1]  # ✅ ตัด `/` ท้าย URL ออก
    print(f"🌐 Domain: {domain}")
    # ✅ ดึงข้อมูลสมาชิกทั่วไป (ที่ไม่มี InstructorProfile)
    members = User.objects.filter(instructor_profile__isnull=True).values(
        "id", "first_name", "last_name", "email"
    )

    # ✅ ดึงข้อมูลผู้สอน พร้อมรายละเอียดเพิ่มเติม
    instructors = InstructorProfile.objects.select_related("user").all()
    instructor_data = [
        {
            "id": instructor.user.id,
            "first_name": instructor.user.first_name,
            "last_name": instructor.user.last_name,
            "email": instructor.user.email,
            "subject": instructor.subject,
            "phone": instructor.phone,
            "profile_picture": f"{domain}{instructor.profile_picture.url}" if instructor.profile_picture else None,
        }
        for instructor in instructors
    ]
    print("👨‍🏫 Instructor Data:", instructor_data)

    return Response(
        {
            "members": list(members),
            "instructors": instructor_data,
        },
        status=200,
    )


@api_view(["POST"])
@permission_classes([AllowAny])  # ✅ อนุญาตให้ทุกคนเรียกใช้ API นี้
def register_instructor_api(request):
    """
    ✅ API สำหรับลงทะเบียนผู้สอน
    """
    data = request.data
    username = data.get("username")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone = data.get("phone")
    age = data.get("age")
    subject = data.get("subject")
    password = data.get("password")
    password2 = data.get("password2")
    profile_picture = request.FILES.get("profile_picture")

    # ✅ ตรวจสอบว่ารหัสผ่านตรงกันหรือไม่
    if password != password2:
        return Response({"error": "รหัสผ่านไม่ตรงกัน"}, status=HTTP_400_BAD_REQUEST)

    # ✅ ตรวจสอบว่าชื่อผู้ใช้หรืออีเมลถูกใช้ไปแล้วหรือไม่
    if User.objects.filter(username=username).exists():
        return Response({"error": "ชื่อผู้ใช้นี้มีอยู่แล้ว"}, status=HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"error": "อีเมลนี้ถูกใช้ไปแล้ว"}, status=HTTP_400_BAD_REQUEST)

    # ✅ สร้าง User ใหม่
    user = User.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=make_password(password),  # 🔹 เข้ารหัสรหัสผ่านก่อนบันทึก
    )

    # ✅ ตรวจสอบและเพิ่มผู้ใช้ไปยังกลุ่ม "Instructor"
    instructor_group, created = Group.objects.get_or_create(name="Instructor")
    user.groups.add(instructor_group)

    # ✅ สร้าง InstructorProfile
    instructor_profile = InstructorProfile.objects.create(
        user=user,
        profile_picture=profile_picture,
        phone=phone,
        age=age,
        subject=subject,
    )

    return Response({"message": "ลงทะเบียนผู้สอนสำเร็จ"}, status=HTTP_201_CREATED)



# ✅ API ดึงแบนเนอร์ที่รออนุมัติ (Admin Only)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def banners_admin_api(request):
    banners = Banner.objects.filter(status="pending")
    banners_data = [
        {
            'id': banner.id,
            'image_url': request.build_absolute_uri(banner.image.url) if banner.image else None,
            'created_at': banner.created_at.strftime('%d/%m/%Y %H:%M')
        }
        for banner in banners
    ]
    return Response(banners_data, status=status.HTTP_200_OK)


# ✅ API อนุมัติแบนเนอร์ (Admin Only)
@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def Admin_approve_banner_api(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    banner.status = "approved"
    banner.rejection_message = ""
    banner.save()
    return Response({"message": "✅ อนุมัติโฆษณาสำเร็จ!"}, status=status.HTTP_200_OK)


# ✅ API ปฏิเสธแบนเนอร์ (Admin Only)
@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def Admin_reject_banner_api(request, banner_id):
    try:
        data = json.loads(request.body)
        rejection_message = data.get("rejection_message", "")

        banner = get_object_or_404(Banner, id=banner_id)
        banner.status = "rejected"
        banner.rejection_message = rejection_message
        banner.save()

        return Response({"message": "⛔ ปฏิเสธโฆษณาสำเร็จ!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # ต้องล็อกอินเพื่อใช้งาน API
def api_upload_payment_qr(request, course_id):
    """
    ✅ API สำหรับอัปโหลด QR Code การชำระเงิน
    """
    course = get_object_or_404(Course, id=course_id)

    if "payment_qr" not in request.FILES:
        return Response({"error": "⚠️ กรุณาอัปโหลดไฟล์ QR Code"}, status=status.HTTP_400_BAD_REQUEST)

    payment_qr = request.FILES["payment_qr"]
    fs = FileSystemStorage()
    filename = fs.save(payment_qr.name, payment_qr)

    # ✅ บันทึกไฟล์ลงฐานข้อมูล
    course.payment_qr = filename
    course.save()

    return Response({"message": "✅ อัปโหลด QR Code สำเร็จแล้ว!"}, status=status.HTTP_200_OK)

# ✅ API ดึงคอร์สที่รออนุมัติ (pending, revised)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_review_booking_courses(request):
    courses = Course.objects.filter(status__in=['pending', 'revised'])
    serializer = CourseSerializer(courses, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ API อนุมัติคอร์ส (Admin Only)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_approve_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not course.payment_qr:
        return Response({"error": "❌ กรุณาอัปโหลด QR Code ก่อนอนุมัติ"}, status=status.HTTP_400_BAD_REQUEST)

    course.status = 'approved'
    course.save()
    
    return Response({"message": "✅ อนุมัติคอร์สเรียนสำเร็จ!"}, status=status.HTTP_200_OK)


# ✅ API ส่งคอร์สกลับไปแก้ไข (Admin Only)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_send_back_course(request, course_id):
    try:
        data = request.data
        revision_message = data.get("revision_message", "")

        course = get_object_or_404(Course, id=course_id)
        course.status = 'revision'
        course.revision_message = revision_message
        course.save()

        return Response({"message": "⛔ ส่งคอร์สกลับไปแก้ไขสำเร็จ!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])  # ต้องล็อกอินก่อนใช้งาน API
def update_booking_status_api(request, booking_id):
    """
    อัปเดตสถานะการจองของผู้ใช้ (ใช้สำหรับโมบาย)
    """
    booking = get_object_or_404(CourseBooking, id=booking_id)

    # ✅ ตรวจสอบค่า 'status' ที่ถูกส่งมาจาก Request
    new_status = request.data.get("status")
    if new_status not in ["confirmed", "rejected"]:
        return Response({"error": "สถานะไม่ถูกต้อง"}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ อัปเดตสถานะการจอง
    booking.booking_status = new_status
    booking.save()

    # ✅ ส่งข้อความแจ้งเตือน
    messages.success(request, f"อัปเดตสถานะเป็น {booking.get_booking_status_display()} สำเร็จ!")

    return Response(
        {"message": f"อัปเดตสถานะเป็น {booking.get_booking_status_display()} สำเร็จ!"},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_api(request):
    """ API สำหรับดึงข้อมูลสรุปรายได้รวม (สำหรับแอดมินในแอปมือถือ) """
    
    today = datetime.today().date()

    # ✅ คำนวณจำนวนคอร์สที่ถูกจองและคอร์สวิดีโอที่ถูกซื้อ
    total_booking_courses = CourseBooking.objects.filter(booking_status="confirmed").count()
    total_video_courses = VideoCourseOrder.objects.filter(payment_status="confirmed").count()

    # ✅ ดึงราคาคอร์สวิดีโอเพื่อนำไปคำนวณ
    video_courses = VideoCourse.objects.values_list('id', 'price')
    video_prices = {course_id: price for course_id, price in video_courses}

    # ✅ คำนวณรายได้รวมจากทั้งสองประเภทคอร์ส
    total_income = (
        CourseBooking.objects.filter(booking_status="confirmed").aggregate(total=Sum('course__price'))['total'] or 0
    ) + (
        sum(
            video_prices.get(order.course_id, 0)
            for order in VideoCourseOrder.objects.filter(payment_status="confirmed")
        )
    )

    # ✅ รายได้แยกตามประเภท
    booking_income = CourseBooking.objects.filter(booking_status="confirmed").aggregate(total=Sum('course__price'))['total'] or 0
    video_income = sum(
        video_prices.get(order.course_id, 0)
        for order in VideoCourseOrder.objects.filter(payment_status="confirmed")
    )

    # ✅ รายได้จากแต่ละคอร์ส
    course_revenues = []

    # ✅ รายได้จากคอร์สจอง
    courses = CourseBooking.objects.filter(booking_status="confirmed").values('course__title').annotate(
        total_income=Sum('course__price'), total_students=Count('id')
    )
    for course in courses:
        course_revenues.append({
            "title": course['course__title'],
            "type": "คอร์สจอง",
            "total_students": course['total_students'],
            "revenue": course['total_income']
        })

    # ✅ รายได้จากคอร์สวิดีโอ
    video_revenues = VideoCourseOrder.objects.filter(payment_status="confirmed").values('course_id').annotate(
        total_students=Count('course_id')
    )
    for course in video_revenues:
        course_revenues.append({
            "title": VideoCourse.objects.get(id=course['course_id']).title,
            "type": "คอร์สวิดีโอ",
            "total_students": course['total_students'],
            "revenue": video_prices.get(course['course_id'], 0) * course['total_students']
        })

    # ✅ รายได้แยกตามเดือน
    monthly_income = []
    thai_months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
                   "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
    
    for month in range(1, 13):
        monthly_booking = CourseBooking.objects.filter(
            booking_status="confirmed",
            booking_date__month=month
        ).aggregate(total=Sum('course__price'))['total'] or 0

        monthly_video = sum(
            video_prices.get(order.course_id, 0)
            for order in VideoCourseOrder.objects.filter(payment_status="confirmed", payment_date__month=month)
        )

        monthly_total = monthly_booking + monthly_video
        monthly_income.append({
            "month": thai_months[month - 1],
            "total_income": monthly_total
        })

    return Response({
        "total_income": total_income,
        "booking_income": booking_income,
        "video_income": video_income,
        "total_booking_courses": total_booking_courses,
        "total_video_courses": total_video_courses,
        "course_revenues": course_revenues,
        "monthly_income": monthly_income,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def course_revenue_api(request):
    """ API ดึงข้อมูลรายได้จากคอร์สทั้งหมด """

    course_revenues = []
    courses = CourseBooking.objects.filter(booking_status="confirmed").values('course__title').annotate(
        total_income=Sum('course__price'), total_students=Count('id')
    )

    for course in courses:
        course_revenues.append({
            "title": course['course__title'],
            "type": "คอร์สจอง",
            "total_students": course['total_students'],
            "revenue": course['total_income']
        })

    video_courses = VideoCourse.objects.values_list('name', 'price')
    video_prices = {name: price for name, price in video_courses}

    video_revenues = CourseOrder.objects.filter(status="paid").values('course_name').annotate(
        total_students=Count('course_name')
    )

    for course in video_revenues:
        course_revenues.append({
            "title": course['course_name'],
            "type": "คอร์สวิดีโอ",
            "total_students": course['total_students'],
            "revenue": video_prices.get(course['course_name'], 0) * course['total_students']
        })

    return Response({"course_revenues": course_revenues})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_income_api(request):
    """ API สำหรับดึงข้อมูลรายได้แยกตามเดือน """

    monthly_income = []
    thai_months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
                   "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]

    video_courses = VideoCourse.objects.values_list('id', 'price')
    video_prices = {course_id: price for course_id, price in video_courses}

    for month in range(1, 13):
        monthly_booking = CourseBooking.objects.filter(
            booking_status="confirmed",
            booking_date__month=month
        ).aggregate(total=Sum('course__price'))['total'] or 0

        monthly_video = sum(
            video_prices.get(order.course_id, 0)
            for order in VideoCourseOrder.objects.filter(payment_status="confirmed", payment_date__month=month)
        )

        monthly_total = monthly_booking + monthly_video
        monthly_income.append({
            "month": thai_months[month - 1],
            "total_income": monthly_total
        })

    return Response({"monthly_income": monthly_income})


# ✅ ฟังก์ชันสร้าง PIN 6 หลัก
def generate_pin():
    return ''.join(random.choices(string.digits, k=6))


# ✅ 1. API ขอรหัส PIN รีเซ็ตรหัสผ่าน
@api_view(["POST"])
@permission_classes([AllowAny])
def request_reset_password_api(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "กรุณาระบุอีเมล"}, status=400)

    try:
        user = User.objects.get(email=email)
        pin = generate_pin()
        expires_at = now() + timedelta(minutes=5)

        # ✅ บันทึก PIN ใน session
        request.session["reset_pin"] = {"pin": pin, "expires_at": expires_at.isoformat()}
        request.session["reset_email"] = email

        # ✅ ส่ง PIN ทางอีเมล
        send_mail(
            "รหัส PIN รีเซ็ตรหัสผ่าน",
            f"รหัส PIN ของคุณคือ {pin} (หมดอายุใน 5 นาที)",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({"message": "รหัส PIN ถูกส่งไปยังอีเมลของคุณแล้ว"})
    except User.DoesNotExist:
        return Response({"error": "ไม่พบอีเมลนี้ในระบบ"}, status=404)


# ✅ 2. API ตรวจสอบรหัส PIN
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_reset_password_api(request):
    entered_pin = request.data.get("pin")
    if not entered_pin:
        return Response({"error": "กรุณากรอกรหัส PIN"}, status=400)

    session_data = request.session.get("reset_pin", {})

    if not session_data:
        return Response({"error": "รหัส PIN หมดอายุ กรุณาขอใหม่"}, status=400)

    stored_pin = session_data.get("pin")
    expires_at = session_data.get("expires_at")

    # ✅ ตรวจสอบ PIN หมดอายุหรือไม่
    if expires_at and now() > datetime.datetime.fromisoformat(expires_at):
        del request.session["reset_pin"]
        return Response({"error": "รหัส PIN หมดอายุ กรุณาขอใหม่"}, status=400)

    # ✅ ตรวจสอบ PIN ถูกต้องหรือไม่
    if entered_pin == stored_pin:
        return Response({"message": "รหัส PIN ถูกต้อง"})
    else:
        return Response({"error": "รหัส PIN ไม่ถูกต้อง"}, status=400)


# ✅ ฟังก์ชันตรวจสอบความแข็งแกร่งของรหัสผ่าน
def is_valid_password(password):
    return len(password) >= 8 and re.search(r"[0-9]", password)


# ✅ 3. API ตั้งรหัสผ่านใหม่
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_api(request):
    new_password = request.data.get("new_password")
    confirm_password = request.data.get("confirm_password")

    if not new_password or not confirm_password:
        return Response({"error": "กรุณากรอกรหัสผ่านทั้งสองช่อง"}, status=400)

    if new_password != confirm_password:
        return Response({"error": "รหัสผ่านไม่ตรงกัน"}, status=400)

    if not is_valid_password(new_password):
        return Response({"error": "รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัว และมีตัวเลข"}, status=400)

    email = request.session.get("reset_email")
    if not email:
        return Response({"error": "ไม่พบข้อมูลอีเมล กรุณาขอ PIN ใหม่"}, status=400)

    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        # ✅ ล้างข้อมูล PIN ออกจาก session
        request.session.pop("reset_pin", None)
        request.session.pop("reset_email", None)

        return Response({"message": "เปลี่ยนรหัสผ่านสำเร็จ"})
    except User.DoesNotExist:
        return Response({"error": "ไม่พบบัญชีผู้ใช้"}, status=404)


#---------------------------------------------api แอดมิน --------------------------------------------------------


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_api(request):
    """
    API สำหรับดึงข้อมูลโปรไฟล์ของผู้ใช้ที่ล็อกอินอยู่
    """
    user = request.user
    profile = user.profile
    data = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
        
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_api(request):
    """
    API สำหรับอัปเดตโปรไฟล์ของผู้ใช้ที่ล็อกอินอยู่
    """
    user = request.user
    profile = user.profile

    user.username = request.data.get('username', user.username)
    user.first_name = request.data.get('first_name', user.first_name)
    user.last_name = request.data.get('last_name', user.last_name)
    user.email = request.data.get('email', user.email)
    
    if 'profile_picture' in request.FILES:
        if profile.profile_picture:
            profile.profile_picture.delete()  # ลบไฟล์รูปเก่าก่อนอัปโหลดใหม่
        profile.profile_picture = request.FILES['profile_picture']

    user.save()
    profile.save()

    return Response({"message": "อัปเดตโปรไฟล์สำเร็จ"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def course_details_api(request, course_id):
    """
    API สำหรับดึงรายละเอียดคอร์สตาม `course_id`
    """
    course_details = get_object_or_404(CourseDetails, course_id=course_id)  # ดึงข้อมูล CourseDetails
    add_course = course_details.course  # ดึงข้อมูล add_course ที่เป็น ForeignKey

    def build_full_url(image_field):
        """ แปลง Path เป็น URL เต็ม """
        if image_field and hasattr(image_field, 'url'):
            return request.build_absolute_uri(image_field.url)
        return None

    # สร้าง URL เต็มของรูปภาพหลักและเพิ่มเติม
    course_data = CourseDetailsSerializer(course_details).data
    add_course_data = AddCourseSerializer(add_course).data

    course_data["image"] = build_full_url(course_details.image)
    course_data["additional_image"] = build_full_url(course_details.additional_image)
    course_data["extra_image_1"] = build_full_url(course_details.extra_image_1)
    course_data["extra_image_2"] = build_full_url(course_details.extra_image_2)
    
    add_course_data["image"] = build_full_url(add_course.image)

    return Response({
        "course_details": course_data,
        "add_course": add_course_data
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_submit_booking(request, course_id):
    """
    API สำหรับจองคอร์สเรียน
    """
    course_details = get_object_or_404(CourseDetails, course_id=course_id)
    course_selected = course_details.course

    data = request.data
    selected_course = data.get("selected_course", "").strip()

    if not selected_course:
        return Response({"error": "กรุณาเลือกคอร์สก่อนดำเนินการต่อ"}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ ดึงข้อมูลจาก API Request
    booking = CourseBooking.objects.create(
        user=request.user,
        student_name=data.get("student_name", ""),
        student_name_en=data.get("student_name_en", ""),
        nickname_th=data.get("nickname_th", ""),
        nickname_en=data.get("nickname_en", ""),
        age=data.get("age", ""),
        grade=data.get("grade", ""),
        other_grade=data.get("other_grade", ""),
        parent_nickname=data.get("parent_nickname", ""),
        phone=data.get("phone", ""),
        line_id=data.get("line_id", ""),
        course=course_selected,
        selected_course=selected_course,
        booking_status="pending",
        payment_status="pending"
    )

    return Response({
        "message": "✅ การจองสำเร็จ! โปรดดำเนินการชำระเงิน",
        "booking_id": booking.id
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_payment_details(request, booking_id):
    """
    API สำหรับดึงรายละเอียดการชำระเงิน
    """
    booking = get_object_or_404(CourseBooking, id=booking_id, user=request.user)
    course_details = get_object_or_404(CourseDetails, course=booking.course)
    course = course_details.course

    qr_code_url = request.build_absolute_uri(course.payment_qr.url) if course.payment_qr else None
    
    

    return Response({
        "booking_id": booking.id,
        "course_name": course.title,
        "course_price": course.price,
        "qr_code_url": qr_code_url,
        "payment_status": booking.payment_status
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_submit_payment(request, booking_id):
    """
    API สำหรับอัปโหลดสลิปการชำระเงิน
    """
    booking = get_object_or_404(CourseBooking, id=booking_id, user=request.user)

    if "payment_slip" not in request.FILES:
        return Response({"error": "กรุณาอัปโหลดไฟล์สลิป"}, status=status.HTTP_400_BAD_REQUEST)

    payment_slip = request.FILES["payment_slip"]
    fs = FileSystemStorage()
    filename = fs.save(payment_slip.name, payment_slip)

    # ✅ บันทึกไฟล์ลงฐานข้อมูล
    booking.payment_slip = filename
    booking.payment_status = "pending"
    booking.save()

    return Response({"message": "✅ อัปโหลดสลิปสำเร็จ! กรุณารอการตรวจสอบ"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_booking_status(request, booking_id):
    """
    API สำหรับตรวจสอบสถานะการจอง
    """
    booking = get_object_or_404(CourseBooking, id=booking_id, user=request.user)
    return Response({
        "booking_id": booking.id,
        "booking_status": booking.booking_status,
        "payment_status": booking.payment_status
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_bookings(request):
    """
    API สำหรับดึงประวัติการจองของผู้ใช้
    """
    bookings = CourseBooking.objects.filter(user=request.user)
    serializer = CourseBookingSerializer(bookings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_courses_api(request):
    """API สำหรับดึงคอร์สที่ผู้ใช้จอง และคอร์สวิดีโอที่ซื้อ"""
    
    # ✅ ดึงข้อมูลคอร์สที่จอง
    bookings = CourseBooking.objects.filter(user=request.user).order_by("-booking_date")
    response_data = []

    for booking in bookings:
        course_data = CourseSerializer(booking.course, context={'request': request}).data
        booking_data = CourseBookingSerializer(booking, context={'request': request}).data
        booking_data["course"] = course_data
        booking_data["type"] = "live_course"  # ✅ เพิ่มประเภทคอร์ส
        response_data.append(booking_data)

    # ✅ ดึงข้อมูลคอร์สวิดีโอที่ซื้อ
    purchased_video_courses = VideoCourseOrder.objects.filter(user=request.user).order_by("-payment_date")

    for video_course in purchased_video_courses:
        video_course_data = VideoCourseOrderSerializer(video_course, context={'request': request}).data
        response_data.append({
            "id": video_course.id,
            "type": "video_course",  # ✅ เพิ่มประเภทคอร์สวิดีโอ
            "video_course": video_course_data,
            "purchased_date": video_course.payment_date,
        })

    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_my_courses_api(request, course_id):
    """API สำหรับดึงรายละเอียดของการจองคอร์ส (เฉพาะของตนเอง)"""
    course = get_object_or_404(Course, id=course_id)

    # ✅ ตรวจสอบให้แน่ใจว่าแสดงเฉพาะข้อมูลของผู้ใช้ที่ล็อกอิน
    bookings = CourseBooking.objects.filter(course=course, user=request.user).order_by("-booking_date")

    if not bookings.exists():
        return Response({"error": "คุณไม่มีสิทธิ์ดูข้อมูลการจองนี้"}, status=403)

    return Response({
        "course": CourseSerializer(course, context={'request': request}).data,
        "bookings": BookingDetailSerializer(bookings, many=True, context={'request': request}).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_booking_history_api(request):
    """API สำหรับดึงประวัติการจองของผู้ใช้ที่ล็อกอินอยู่ (เฉพาะของตนเอง)"""
    bookings = CourseBooking.objects.filter(user=request.user).order_by("-booking_date")
    serializer = BookingHistorySerializer(bookings, many=True, context={'request': request})

    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_password_api(request):
    """
    API สำหรับตรวจสอบรหัสผ่านเก่าก่อนเปลี่ยนรหัสผ่าน
    """
    try:
        # ✅ ใช้ request.data.get() แทน request.POST
        current_password = request.data.get("current_password")  
        
        if not current_password:
            return Response({"error": "❌ กรุณากรอกรหัสผ่านเดิม"}, status=400)

        # ✅ ใช้ request.user เช็ค password อย่างถูกต้อง
        if request.user.check_password(current_password):
            return Response({"message": "✅ รหัสผ่านถูกต้อง", "can_change": True}, status=200)
        else:
            return Response({"error": "❌ รหัสผ่านไม่ถูกต้อง"}, status=400)

    except Exception as e:
        return Response({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_api(request):
    """
    API สำหรับเปลี่ยนรหัสผ่านใหม่
    """
    user = request.user
    new_password = request.data.get('new_password')
    confirm_new_password = request.data.get('confirm_new_password')

    if not new_password or not confirm_new_password:
        return Response({"error": "กรุณากรอกรหัสผ่านใหม่และยืนยันรหัสผ่าน"}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_new_password:
        return Response({"error": "❌ รหัสผ่านใหม่และการยืนยันรหัสผ่านไม่ตรงกัน"}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ ตั้งค่ารหัสผ่านใหม่
    user.set_password(new_password)
    user.save()

    # ✅ อัปเดต session auth เพื่อป้องกันการล็อกเอาต์
    update_session_auth_hash(request, user)

    return Response({"message": "✅ เปลี่ยนรหัสผ่านสำเร็จ"}, status=status.HTTP_200_OK)

#-----------------------------------------------------------------สำหรับ API ------------------------------------------------------------------------------------------------------------------------------------------------------------------



def sales(request):
    active_tab = request.GET.get("type", "booking")

    # ✅ คอร์สเรียนแบบจองที่มีการจอง
    booked_courses = Course.objects.filter(
        id__in=CourseBooking.objects.values("course_id")
    ).annotate(booking_count=Count("coursebooking"))

    # ✅ หา CourseDetails ที่เกี่ยวข้อง
    course_details_dict = {cd.course_id: cd for cd in CourseDetails.objects.filter(course__in=booked_courses)}

    # ✅ คอร์สเรียนแบบวิดีโอที่มีการซื้อ
    purchased_courses = VideoCourse.objects.filter(
        id__in=VideoCourseOrder.objects.values("course_id")  # แก้ให้ใช้ VideoCourseOrder
    ).annotate(purchase_count=Count("videocourseorder"))  # ใช้ related_name ที่ถูกต้อง

    return render(request, "admin/sales.html", {
        "booked_courses": booked_courses,
        "course_details_dict": course_details_dict,  
        "purchased_courses": purchased_courses,  # ✅ ส่งคอร์สวิดีโอที่ถูกซื้อไปที่ Template
        "active_tab": active_tab,
    })


def booking_detail(request, course_id):
    # ✅ ดึง Course จาก `course_id`
    course = get_object_or_404(Course, id=course_id)

    search_query = request.GET.get("search", "")

    # ✅ ดึงข้อมูลการจองจาก `CourseBooking`
    bookings = CourseBooking.objects.filter(course=course).order_by("-booking_date")

    if search_query:
        bookings = bookings.filter(student_name__icontains=search_query)

    paginator = Paginator(bookings, 10)
    page_number = request.GET.get("page")
    bookings_page = paginator.get_page(page_number)

    return render(request, "admin/booking_detail.html", {
        "course": course,
        "bookings": bookings_page,
    })





def upload_payment_qr(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST" and 'payment_qr' in request.FILES:
        course.payment_qr = request.FILES['payment_qr']
        course.save()
        messages.success(request, "✅ อัปโหลด QR Code สำเร็จแล้ว!")
        return redirect('review_booking_courses')

    messages.error(request, "⚠️ กรุณาอัปโหลดไฟล์ QR Code")
    return redirect('review_booking_courses')

def review_booking_courses(request):
    # ดึงเฉพาะคอร์สที่มีสถานะ 'pending' หรือ 'revised'
    courses = Course.objects.filter(status__in=['pending', 'revised'])
    return render(request, 'admin/review_booking_courses.html', {'courses': courses})


def delete_selected_courses(request):
    if request.method == 'POST':
        # ดึงรายการ ID คอร์สที่ถูกเลือกจาก checkbox
        selected_ids = request.POST.getlist('selected_courses')

        if selected_ids:
            # ลบคอร์สทั้งหมดที่มี ID ตรงกับรายการที่เลือก
            courses_to_delete = Course.objects.filter(id__in=selected_ids)

            # ลบคอร์สและรายละเอียดคอร์สที่เกี่ยวข้อง
            for course in courses_to_delete:
                course.delete()

            messages.success(request, f"ลบคอร์สที่เลือกจำนวน {len(selected_ids)} รายการเรียบร้อยแล้ว!")
        else:
            messages.error(request, "กรุณาเลือกรายการที่ต้องการลบ")
    
    # กลับไปยังหน้าคอร์สเรียนแบบจอง
    return redirect('reservation_courses')

def approve_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not course.payment_qr:
        messages.error(request, "❌ กรุณาอัปโหลด QR Code ก่อนอนุมัติ")
        return redirect('review_booking_courses')

    course.status = 'approved'  # เปลี่ยนสถานะเป็นอนุมัติ
    course.save()
    messages.success(request, 'อนุมัติคอร์สเรียนเรียบร้อยแล้ว!')
    return redirect('review_booking_courses')  # กลับไปยังหน้าตรวจสอบคอร์ส




def send_back_course(request, course_id):
    if request.method == 'POST':
        revision_message = request.POST.get('revision_message')

        # ดึงข้อมูลคอร์สและอัปเดตสถานะ
        course = get_object_or_404(Course, id=course_id)
        course.status = 'revision'  # เปลี่ยนสถานะเป็น "revision"
        course.revision_message = revision_message  # บันทึกข้อความที่แอดมินส่งกลับ
        course.save()

        messages.success(request, 'ส่งคอร์สกลับไปแก้ไขเรียบร้อยแล้ว!')
        return redirect('review_booking_courses')
    else:
        # กรณี GET method
        return HttpResponseRedirect(reverse('review_booking_courses'))
    

from django.db.models import Case, When, Count, Sum, DecimalField, OuterRef, Subquery, Value, F

def generate_graphs(booking_income_query, video_income_query, filter_type, course_type):
    """ ฟังก์ชันสร้างกราฟรายได้ตามคอร์สและรายได้แยกตามวันหรือเดือน """
    
    course_names = []
    course_earnings = []

    # ✅ กรองตามฟิลเตอร์
    if filter_type == "daily":
        today = datetime.today().date()
        booking_income_query = booking_income_query.filter(booking_date=today)
        video_income_query = video_income_query.filter(payment_date=today)
    elif filter_type == "monthly":
        today = datetime.today()
        booking_income_query = booking_income_query.filter(booking_date__month=today.month)
        video_income_query = video_income_query.filter(payment_date__month=today.month)

    # ✅ **สร้างกราฟรายได้จากคอร์สจอง**
    if course_type in ["all", "booking"]:
        course_booking_totals = (
            booking_income_query.values('course__title')
            .annotate(total_income=Sum('course__price'))
        )
        for booking in course_booking_totals:
            course_names.append(booking['course__title'])
            course_earnings.append(booking['total_income'])

    # ✅ **สร้างกราฟรายได้จากคอร์สวิดีโอ**
    if course_type in ["all", "video"]:
        video_courses = VideoCourse.objects.values_list('id', 'price')  # ดึง 'id' แทน 'title'
        video_prices = {course_id: price for course_id, price in video_courses}

        course_video_totals = (
            video_income_query.values('course_id')
            .annotate(total_count=Count('course_id'))
        )

        for order in course_video_totals:
            course_id = order['course_id']
            total_students = order['total_count']
            total_income = video_prices.get(course_id, 0) * total_students
            course_name = VideoCourse.objects.get(id=course_id).title
            course_names.append(course_name)
            course_earnings.append(total_income)

    # ✅ สร้างกราฟแท่งแสดงรายได้แต่ละคอร์ส
    course_chart = go.Bar(
        x=course_names,
        y=course_earnings,
        marker=dict(color="#1E3A8A"),
        name="รายได้แต่ละคอร์ส",
        hoverinfo="x+y",
        text=course_earnings,
        textposition="outside",
        textfont=dict(size=14, color="black")
    )

    layout = go.Layout(
        title=dict(
            text="รายได้จากแต่ละคอร์ส",
            font=dict(size=18, color="#4A5568"),
            x=0.5
        ),
        xaxis=dict(
            title="ชื่อคอร์ส",
            tickangle=-20,
            showgrid=True,
        ),
        yaxis=dict(
            title="รายได้รวม (บาท)",
            gridcolor="#E2E8F0"
        ),
        height=500,
        margin=dict(t=50, b=100)
    )

    fig_course = go.Figure(data=[course_chart], layout=layout)
    graph_course_div = opy.plot(fig_course, auto_open=False, output_type="div")

    # ✅ **สร้างกราฟรายได้แยกตามเดือนหรือวัน**
    thai_months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]

    monthly_income = []
    month_labels = []

    for month in range(1, 13):
        monthly_booking = booking_income_query.filter(
            booking_date__month=month
        ).aggregate(total=Sum('course__price'))['total'] or 0

        monthly_video = sum(
            video_prices.get(order['course_id'], 0) * order['total_count']
            for order in video_income_query.filter(payment_date__month=month)
            .values('course_id')
            .annotate(total_count=Count('course_id'))
        )

        monthly_total = monthly_booking + monthly_video
        monthly_income.append(monthly_total)
        month_labels.append(thai_months[month - 1])

    monthly_chart = go.Bar(
        x=month_labels,
        y=monthly_income,
        marker=dict(color="#10B981"),
        name="รายได้แต่ละเดือน",
        hoverinfo="x+y",
        text=monthly_income,
        textposition="outside",
        textfont=dict(size=12, color="black")
    )

    layout_monthly = go.Layout(
        title=dict(text="รายได้แยกตามเดือน", font=dict(size=18, color="#4A5568"), x=0.5),
        xaxis=dict(title="เดือน", showgrid=False),
        yaxis=dict(title="รายได้รวม (บาท)", gridcolor="#E2E8F0"),
        height=500,
        margin=dict(t=50, b=100)
    )

    fig_monthly = go.Figure(data=[monthly_chart], layout=layout_monthly)
    graph_monthly_div = opy.plot(fig_monthly, auto_open=False, output_type="div")

    return graph_course_div, graph_monthly_div


def admin_dashboard(request):
    filter_type = request.GET.get("filter", "all")
    course_type = request.GET.get("course_type", "all")

    today = datetime.today().date()

    # ✅ **ดึงค่ารายได้รวมทั้งหมด (ไม่ใช้ฟิลเตอร์)**
    total_booking_courses = CourseBooking.objects.filter(booking_status="confirmed").count()
    total_video_courses = VideoCourseOrder.objects.filter(payment_status="confirmed").count()
    
    total_income = (
        CourseBooking.objects.filter(booking_status="confirmed").aggregate(total=Sum('course__price'))['total'] or 0
    ) + (
        sum(
            VideoCourse.objects.filter(id=order.course_id).first().price
            if VideoCourse.objects.filter(id=order.course_id).exists() else 0
            for order in VideoCourseOrder.objects.filter(payment_status="confirmed")
        )
    )
    
    booking_income = CourseBooking.objects.filter(booking_status="confirmed").aggregate(total=Sum('course__price'))['total'] or 0
    
    video_income = sum(
        VideoCourse.objects.filter(id=order.course_id).first().price
        if VideoCourse.objects.filter(id=order.course_id).exists() else 0
        for order in VideoCourseOrder.objects.filter(payment_status="confirmed")
    )

    # ✅ **ฟิลเตอร์ข้อมูลตามที่เลือก (ใช้กับตารางและกราฟเท่านั้น)**
    booking_income_query = CourseBooking.objects.filter(booking_status="confirmed")
    video_income_query = VideoCourseOrder.objects.filter(payment_status="confirmed")

    if course_type == "video":
        booking_income_query = CourseBooking.objects.none()
    elif course_type == "booking":
        video_income_query = VideoCourseOrder.objects.none()

    if filter_type == "daily":
        booking_income_query = booking_income_query.filter(booking_date=today)
        video_income_query = video_income_query.filter(payment_date=today)
    elif filter_type == "monthly":
        booking_income_query = booking_income_query.filter(booking_date__month=today.month)
        video_income_query = video_income_query.filter(payment_date__month=today.month)

    # ✅ **ดึงข้อมูลคอร์สและคำนวณรายได้ (ใช้กับกราฟและตาราง)**
    course_revenues = []
    course_names = []
    course_earnings = []

    # ✅ **ข้อมูลคอร์สแบบจอง**
    if course_type in ["all", "booking"]:
        courses = Course.objects.all()
        for course in courses:
            course_booking_income = CourseBooking.objects.filter(course=course, booking_status="confirmed").aggregate(total=Sum('course__price'))['total'] or 0
            total_students_in_course = CourseBooking.objects.filter(course=course, booking_status="confirmed").count()

            course_revenues.append({
                "title": course.title,  # ✅ ใช้ title แทน name
                "type": "คอร์สจอง",
                "total_students": total_students_in_course,
                "revenue": course_booking_income
            })

            course_names.append(course.title)
            course_earnings.append(course_booking_income)

    if course_type in ["all", "video"]:
        video_courses = VideoCourse.objects.filter(status="approved")  # กรองคอร์สที่ได้รับการอนุมัติ
        for course in video_courses:
            # คำนวณรายได้จากการขายคอร์สวิดีโอโดยตรงจากราคาของ VideoCourse
            course_video_income = sum(
                order.course.price for order in VideoCourseOrder.objects.filter(course=course, payment_status="confirmed")
            )
            total_students_in_course = VideoCourseOrder.objects.filter(course=course, payment_status="confirmed").count()

            course_revenues.append({
                "title": course.title,  # ใช้ title แทน name
                "type": "คอร์สวิดีโอ",
                "total_students": total_students_in_course,
                "revenue": course_video_income
            })

            course_names.append(course.title)
            course_earnings.append(course_video_income)

    # ✅ **สร้างกราฟ**
    graph_course_div, graph_monthly_div = generate_graphs(
    booking_income_query, video_income_query, filter_type, course_type
)


    context = {
    "total_income": total_income,
    "video_income": video_income,
    "booking_income": booking_income,
    "total_booking_courses": total_booking_courses,
    "total_video_courses": total_video_courses,
    "course_revenues": course_revenues,  # ส่งข้อมูลคอร์สไปยังเทมเพลต
    "filter_type": filter_type,
    "course_type": course_type,
    "graph_course_div": graph_course_div,
    "graph_monthly_div": graph_monthly_div,
}

    return render(request, "admin/dashboard_admin.html", context)

@login_required
def add_banner(request):
    if request.method == 'POST':
        image = request.FILES.get('banner_image')

        if image:
            Banner.objects.create(
                instructor=request.user,  # ✅ ระบุว่าใครเป็นคนเพิ่ม
                image=image,
                status='pending'  # ✅ ตั้งค่ารออนุมัติ
            )
            messages.success(request, "✅ เพิ่มเบนเนอร์สำเร็จ! โปรดรอการอนุมัติจากแอดมิน")
            return redirect('banners')
        else:
            messages.error(request, "⚠ กรุณาเลือกไฟล์รูปภาพ")
    
    return render(request, 'instructor/add_banner.html')

@login_required
def banners(request):
    banners = Banner.objects.filter(instructor=request.user)  # ✅ แสดงเฉพาะของผู้สอนคนนั้น
    return render(request, 'instructor/banners.html', {'banners': banners})

@login_required
@admin_required
def banners_admin(request):
    banners = Banner.objects.filter(status='pending')  # ✅ ดึงเฉพาะที่รออนุมัติ
    return render(request, 'admin/banners_admin.html', {'banners': banners})

@login_required
@admin_required
def approve_banner(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    banner.status = 'approved'
    banner.rejection_message = ""  # ✅ เคลียร์ข้อความปฏิเสธ
    banner.save()
    messages.success(request, "อนุมัติโฆษณาสำเร็จ!")
    return redirect('banners_admin')

@login_required
@admin_required
def reject_banner(request, banner_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rejection_message = data.get('rejection_message', '')

            banner = get_object_or_404(Banner, id=banner_id)
            banner.status = 'rejected'
            banner.rejection_message = rejection_message
            banner.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


def delete_banner(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    banner.delete()
    messages.success(request, "ลบเบนเนอร์สำเร็จ!")
    return redirect('banners')





@instructor_required
def add_course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        additional_description = request.POST.get('additional_description')
        image = request.FILES.get('image')
        additional_image = request.FILES.get('additional_image')
        extra_image_1 = request.FILES.get('extra_image_1')  
        extra_image_2 = request.FILES.get('extra_image_2')

        # บันทึกข้อมูลรายละเอียดคอร์ส
        course_details = CourseDetails(
            course=course,
            name=name,
            description=description,
            additional_description=additional_description,
            image=image,
            additional_image=additional_image,
            extra_image_1=extra_image_1,  # เพิ่มฟิลด์รูปภาพเพิ่มเติม 1
            extra_image_2=extra_image_2,
        )
        course_details.save()

        messages.success(request, "เพิ่มรายละเอียดคอร์สสำเร็จ!")
        return redirect('reservation_courses')

    return render(request, 'instructor/add_course_details.html', {'course': course})

def course_details(request, course_id):
    # ดึง CourseDetails ตาม course_id
    course = get_object_or_404(CourseDetails, course_id=course_id)
    add_course = course.course  # สมมติว่า CourseDetails มี ForeignKey กับ add_course

    return render(request, 'course_details.html', {'course': course, 'add_course': add_course})



def submit_course_for_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course_details = get_object_or_404(CourseDetails, course=course)

    if request.method == 'POST':
        # เปลี่ยนสถานะคอร์สเป็นรอการตรวจสอบ
        course.status = 'pending'
        course.save()
        messages.success(request, "ส่งคอร์สให้แอดมินตรวจสอบเรียบร้อยแล้ว!")
        return redirect('reservation_courses')

    return render(request, 'instructor/submit_course.html', {
        'course': course,
        'course_details': course_details
    })


@instructor_required
@login_required
def add_course(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        instructor = request.POST.get('instructor')  
        price = request.POST.get('price')
        image = request.FILES.get('image')

        print(f"📌 User adding course: {request.user} (ID: {request.user.id})")  

        if not request.user.is_authenticated:
            print("🚨 ผู้ใช้ไม่ได้ล็อกอิน! added_by จะเป็น NULL")
            return redirect('login')  # ส่งไปล็อกอินก่อน

        course = Course(
            title=title,
            description=description,
            instructor=instructor,
            price=price,
            image=image,
            added_by=request.user  # ✅ บันทึก ID ผู้เพิ่มคอร์ส
        )
        course.save()

        print(f"✅ Added by: {course.added_by} (ID: {course.added_by.id})")  # ✅ ตรวจสอบว่าถูกบันทึกจริงไหม

        messages.success(request, "เพิ่มคอร์สเรียนสำเร็จ! คุณสามารถเพิ่มรายละเอียดคอร์สเรียนต่อได้")
        return redirect('add_course_details', course_id=course.id)

    return render(request, 'instructor/add_course.html')



@instructor_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id,added_by=request.user)
    
    if request.method == 'POST':
        # รับค่าจากฟอร์มและบันทึก
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.instructor = request.POST.get('instructor')
        course.price = request.POST.get('price')
        if 'image' in request.FILES:
            course.image = request.FILES['image']
        course.save()
        
        # หลังบันทึกให้เด้งไปยังหน้าแก้ไขรายละเอียดคอร์สเรียน
        return redirect('edit_course_details', course_id=course.id)
    
    return render(request, 'instructor/edit_course.html', {'course': course})


@instructor_required
def edit_course_details(request, course_id):
    # ดึงข้อมูลรายละเอียดคอร์ส
    course_details = get_object_or_404(CourseDetails, course__id=course_id)
    course = course_details.course

    if request.method == "POST":
        # อัปเดตฟิลด์ต่างๆ
        course_details.name = request.POST.get('name', course_details.name)
        course_details.description = request.POST.get('description', course_details.description)
        course_details.additional_description = request.POST.get('additional_description', course_details.additional_description)

        if 'image' in request.FILES:
            course_details.image = request.FILES['image']
        if 'additional_image' in request.FILES:
            course_details.additional_image = request.FILES['additional_image']

        # อัปเดตสถานะคอร์สเป็น "แก้ไขแล้วรอการตรวจสอบ"
        course.status = 'revised'
        course.save()

        course_details.save()

        # ส่งข้อความยืนยัน
        messages.success(request, "รายละเอียดคอร์สถูกบันทึกและส่งไปยังแอดมินตรวจสอบแล้ว")
        return redirect('reservation_courses')

    return render(request, 'instructor/edit_course_details.html', {
        'course_details': course_details,
        'course': course
    })


@instructor_required
def reservation_courses(request):
    courses = Course.objects.filter(added_by=request.user)
    return render(request, 'instructor/reservation_courses.html', {'courses': courses})




def contact(request):
    return render(request, 'contact.html')


def user_list(request):
    members = User.objects.filter(instructor_profile__isnull=True)  # สมาชิกทั่วไป
    instructors = InstructorProfile.objects.select_related('user').all()  # ผู้สอน

    # ✅ Debugging เพื่อตรวจสอบข้อมูลก่อนส่งไปยังเทมเพลต
    print(f"📌 สมาชิกทั้งหมด: {members.count()} | ผู้สอนทั้งหมด: {instructors.count()}")
    for instructor in instructors:
        print(f"👨‍🏫 {instructor.user.first_name} {instructor.user.last_name} | {instructor.subject} | {instructor.phone}")

    return render(request, 'admin/users_teachers.html', {
        'members': members,
        'instructors': instructors
    })



def add_staff(request, user_id):  # รับ user_id เป็นพารามิเตอร์
    """ เพิ่มโปรไฟล์ผู้สอน """

    user = get_object_or_404(User, id=user_id)  # ดึงข้อมูลผู้ใช้จาก User Model

    if request.method == "POST":
        display_name = request.POST.get("display_name")
        subject = request.POST.get("subject")
        image = request.FILES.get("image")

        if display_name and subject:
            # บันทึกข้อมูลลงในตาราง myapp_staff
            new_staff = Staff(name=display_name, subject=subject, image=image)
            new_staff.save()

            messages.success(request, "เพิ่มโปรไฟล์ผู้สอนสำเร็จ!")
            return redirect("user_list")  # กลับไปที่หน้ารายชื่อผู้สอน
        else:
            messages.error(request, "กรุณากรอกข้อมูลให้ครบถ้วน!")

    return render(request, "admin/add_staff.html", {"user": user})




def home(request):
    banners = Banner.objects.filter(status="approved") 
    approved_courses = Course.objects.filter(status='approved', is_closed=False)
    approved_video_courses = VideoCourse.objects.filter(status='approved')

    
    
    if request.user.is_authenticated:
        # Query สำหรับ VideoCourse ที่ผู้ใช้เคยซื้อ
        purchased_video_courses = VideoCourseOrder.objects.filter(user=request.user)
        
        # ดึงเฉพาะ ID ของ VideoCourse ที่เคยซื้อ
        purchased_video_course_ids = list(purchased_video_courses.values_list('course_id', flat=True))

        return render(request, 'home.html', {
            'banners': banners,
            'courses': approved_courses,
            'video_courses': approved_video_courses,
            'purchased_video_courses': purchased_video_courses,
            'purchased_video_course_ids': purchased_video_course_ids,
           

        })  # สำหรับสมาชิก
    
    return render(request, 'guest_home.html', {
        'banners': banners,
        'courses': approved_courses,
        'video_courses': approved_video_courses,  
    })  # สำหรับผู้ที่ยังไม่ได้เป็นสมาชิก


def all_courses(request):
    """ แสดงเฉพาะคอร์สที่ได้รับอนุมัติและยังเปิดรับสมัคร """
    query = request.GET.get('q', '')
    
    # ✅ กรองเฉพาะคอร์สที่ได้รับอนุมัติและยังเปิดรับสมัคร
    approved_courses = Course.objects.filter(status='approved', is_closed=False)  
    approved_video_courses = VideoCourse.objects.filter(status='approved')


    # ✅ ดึงข้อมูล Video Courses ที่ผู้ใช้เคยซื้อ
    if request.user.is_authenticated:
        purchased_video_courses = VideoCourseOrder.objects.filter(user=request.user)
        purchased_video_course_ids = list(purchased_video_courses.values_list('course_id', flat=True))
    else:
        purchased_video_courses = []
        purchased_video_course_ids = []

    if query:
        approved_courses = approved_courses.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
        approved_video_courses = approved_video_courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    template_name = 'all_courses.html' if request.user.is_authenticated else 'guest_all_courses.html'
    return render(request, template_name, {'courses': approved_courses, 'query': query,'video_courses': approved_video_courses,'purchased_video_courses': purchased_video_courses,
        'purchased_video_course_ids': purchased_video_course_ids })


#def all_courses(request):
    # ค้นหาคอร์สที่มีสถานะ 'approved'
    query = request.GET.get('q', '')  # รับค่าค้นหาจากช่องค้นหา
    approved_courses = Course.objects.filter(status='approved',is_closed=False)

    # ✅ ถ้ามีการค้นหา ให้กรองผลลัพธ์
    if query:
        approved_courses = approved_courses.filter(
            Q(title__icontains=query) |  # ค้นหาชื่อคอร์ส
            Q(description__icontains=query)  # ค้นหาจากรายละเอียดคอร์ส
        )

    # ✅ ตรวจสอบว่าผู้ใช้เข้าสู่ระบบหรือไม่
    template_name = 'all_courses.html' if request.user.is_authenticated else 'guest_all_courses.html'

    return render(request, template_name, {'courses': approved_courses, 'query': query})


@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user, 'profile': request.user.profile})


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        profile = user.profile

        user.username = request.POST.get('username', user.username)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()  # ✅ บันทึกการเปลี่ยนแปลง
            
        messages.success(request, "บันทึกข้อมูลเรียบร้อยแล้ว!")
        return redirect('profile')
    
    return render(request, 'edit_profile.html', {'user': request.user, 'profile': request.user.profile})


@login_required
def profile_instructor(request):
    return render(request, 'instructor/profile_instructor.html', {'user': request.user, 'profile': request.user.profile})

@login_required
def update_profile_instructor(request):
    if request.method == 'POST':
        user = request.user
        profile = user.profile

        user.username = request.POST.get('username', user.username)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()  # ✅ บันทึกการเปลี่ยนแปลง
            
        messages.success(request, "บันทึกข้อมูลเรียบร้อยแล้ว!")
        return redirect(reverse('profile_instructor')) 
    
    return render(request, 'instructor/update_profile_instructor.html', {'user': request.user, 'profile': request.user.profile})

@login_required
def logout_view(request):
    logout(request)  # ลบ session ของ User ทั่วไป
    messages.success(request, "ออกจากระบบสำเร็จ")
    return redirect('home')  # ส่งกลับไปยังหน้าแรก

@login_required
@instructor_required
def instructor_logout(request):
    logout(request)  # ลบ session ของ Instructor
    messages.success(request, "คุณได้ออกจากระบบในฐานะผู้สอนแล้ว")
    return redirect('login')  # ส่งกลับไปหน้า Login หรือหน้าที่เหมาะสม

@login_required
def admin_logout(request):
    logout(request)  # ออกจากระบบ
    messages.success(request, "คุณได้ออกจากระบบในฐานะผู้ดูแลระบบแล้ว")
    return redirect('login')  # เปลี่ยนเส้นทางไปยังหน้า Login ของ Admin



def check_password(request):
    return render(request, 'check_password.html')

def verify_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        if request.user.check_password(current_password):
            return redirect('change_password')
        else:
            return render(request, 'check_password.html', {'error_message': 'รหัสผ่านไม่ถูกต้อง'})
    return redirect('check_password')

def change_password(request):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_new_password = request.POST['confirm_new_password']
        if new_password == confirm_new_password:
            request.user.set_password(new_password)
            request.user.save()
            login(request, request.user)  # Log the user back in
            return redirect('profile')
    return render(request, 'change_password.html')


def register_instructor(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        age = request.POST.get("age")
        subject = request.POST.get("subject")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        profile_picture = request.FILES.get("profile_picture")

        # ✅ ตรวจสอบรหัสผ่านตรงกันหรือไม่
        if password != password2:
            messages.error(request, "รหัสผ่านไม่ตรงกัน")
            return redirect("register_instructor")

        # ✅ ตรวจสอบว่ามีชื่อผู้ใช้และอีเมลซ้ำหรือไม่
        if User.objects.filter(username=username).exists():
            messages.error(request, "ชื่อผู้ใช้นี้มีอยู่แล้ว")
            return redirect("register_instructor")
        if User.objects.filter(email=email).exists():
            messages.error(request, "อีเมลนี้ถูกใช้ไปแล้ว")
            return redirect("register_instructor")

        # ✅ สร้าง User
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
        )

        # ✅ ตรวจสอบว่ากลุ่ม "Instructor" มีอยู่หรือไม่ ถ้าไม่มีให้สร้าง
        instructor_group, created = Group.objects.get_or_create(name="Instructor")
        user.groups.add(instructor_group)  # เพิ่มผู้ใช้เข้าในกลุ่ม Instructor

        # ✅ สร้าง InstructorProfile
        instructor_profile = InstructorProfile(
            user=user,
            profile_picture=profile_picture,
            phone=phone,
            age=age,
            subject=subject,
        )
        instructor_profile.save()  # บันทึกข้อมูล

        messages.success(request, "ลงทะเบียนผู้สอนสำเร็จ")
        return redirect("user_list")

    return render(request, "admin/register_instructor.html")


def instructor_list(request):
    instructors = InstructorProfile.objects.select_related('user').all()
    return render(request, 'staff.html', {'instructors': instructors})


def course_details_admin(request, course_id):
    # ดึงข้อมูลคอร์สที่มี id ตรงกับ course_id
    course = get_object_or_404(CourseDetails, course_id=course_id)
    add_course = course.course  # สมมติว่า CourseDetails มี ForeignKey กับ add_course

    # ส่งข้อมูลคอร์สไปที่ Template
    return render(request, 'admin/course_details_admin.html', {'course': course, 'add_course': add_course})

def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(CourseBooking, id=booking_id)

    if status in ["confirmed", "rejected"]:
        booking.booking_status = status
        booking.save()
        
        # ✅ แจ้งเตือนผู้ใช้
        messages.success(request, f"อัปเดตสถานะเป็น {booking.get_booking_status_display()} สำเร็จ!")

    return redirect("booking_detail", course_id=booking.course.id)


def booking_course(request, course_id):
    course = get_object_or_404(CourseDetails, course_id=course_id) 
    return render(request, 'booking_course.html', {'course': course})

@login_required
def submit_booking(request, course_details_id):
    course_details = get_object_or_404(CourseDetails, id=course_details_id)
    course_selected = course_details.course

    if request.method == "POST":
        selected_course = request.POST.get("selected_course", "").strip()

        if not selected_course:
            messages.error(request, "❌ กรุณาเลือกคอร์สก่อนดำเนินการต่อ")
            return redirect("booking_course", course_id=course_details_id)

        # ✅ ดึงข้อมูลจากฟอร์ม
        student_name = request.POST['student_name']
        student_name_en = request.POST['student_name_en']
        nickname_th = request.POST['nickname_th']
        nickname_en = request.POST['nickname_en']
        age = request.POST['age']
        grade = request.POST['grade']
        other_grade = request.POST.get('other_grade', '')
        parent_nickname = request.POST['parent_nickname']
        phone = request.POST['phone']
        line_id = request.POST.get('line_id', '')

        if grade == "อื่นๆ":
            grade = other_grade

        # ✅ บันทึกข้อมูลลง `CourseBooking` และกำหนด `user=request.user`
        booking = CourseBooking.objects.create(
            user=request.user,  # ✅ บันทึก user ที่จองคอร์ส
            student_name=student_name,
            student_name_en=student_name_en,
            nickname_th=nickname_th,
            nickname_en=nickname_en,
            age=age,
            grade=grade,
            other_grade=other_grade,
            parent_nickname=parent_nickname,
            phone=phone,
            line_id=line_id,
            course=course_selected,
            selected_course=selected_course,
            booking_status="pending",
            payment_status="pending"
        )

        return redirect("payment_page", booking_id=booking.id)

    return render(request, "booking_course.html", {"course": course_details})




def payment_page(request, booking_id):
    booking = get_object_or_404(CourseBooking, id=booking_id)  # ✅ ดึงข้อมูลการจอง
    course_details = get_object_or_404(CourseDetails, course=booking.course)

    #course_details = get_object_or_404(CourseDetails, id=booking.course.id)  # ✅ ดึง CourseDetails
    course = course_details.course  # ✅ ดึง Course ที่แท้จริง
    qr_code_url = course.payment_qr.url if course.payment_qr else None  # ✅ ดึง QR Code จาก Course

    return render(request, "payment_page.html", {
        "booking": booking,
        "course": course,  # ✅ ใช้ข้อมูล Course ที่ถูกต้อง
        "qr_code_url": qr_code_url
    })



    
def submit_payment(request, booking_id):
    booking = get_object_or_404(CourseBooking, id=booking_id)

    if request.method == "POST" and "payment_slip" in request.FILES:
        payment_slip = request.FILES["payment_slip"]

        # ✅ บันทึกสลิป
        fs = FileSystemStorage()
        filename = fs.save(payment_slip.name, payment_slip)
        booking.payment_slip = filename
        booking.payment_status = "pending"
        booking.save()

        messages.success(request, "✅ อัปโหลดสลิปสำเร็จ! กรุณารอการตรวจสอบ")
        return redirect("home")  # ✅ พากลับไปหน้าหลัก

    messages.error(request, "⚠ กรุณาอัปโหลดไฟล์สลิป")
    return redirect("payment_page", booking_id=booking.id)

#################################################################################################
@login_required
def instructor_sales(request):
    active_tab = request.GET.get("type", "booking")

    # ✅ คอร์สเรียนแบบจองที่มีการจอง
    booked_courses = Course.objects.filter(
        id__in=CourseBooking.objects.values("course_id"),
        added_by=request.user.id
    ).annotate(booking_count=Count("coursebooking"))

    # ✅ หา CourseDetails ที่เกี่ยวข้อง
    course_details_dict = {
        cd.course_id: cd 
        for cd in CourseDetails.objects.filter(course__in=booked_courses)}

    # ✅ คอร์สเรียนแบบวิดีโอที่มีการซื้อ
    purchased_courses = VideoCourse.objects.filter(
        id__in=VideoCourseOrder.objects.values("course_id"),  # แก้ให้ใช้ VideoCourseOrder
        added_by=request.user.id
    ).annotate(purchase_count=Count("videocourseorder"))  # ใช้ related_name ที่ถูกต้อง

    return render(request, "instructor/sales.html",{
        "booked_courses": booked_courses,
        "course_details_dict": course_details_dict,  
        "purchased_courses": purchased_courses,  # ✅ ส่งคอร์สวิดีโอที่ถูกซื้อไปที่ Template
        "active_tab": active_tab,

    })




@login_required
def instructor_booking_detail(request, course_id):

        # ✅ ดึง Course จาก `course_id`
    course = get_object_or_404(Course, id=course_id)

    search_query = request.GET.get("search", "")

    # ✅ ดึงข้อมูลการจองจาก `CourseBooking`
    bookings = CourseBooking.objects.select_related("user").filter(course=course).order_by("-booking_date")


    if search_query:
        bookings = bookings.filter(student_name__icontains=search_query)

    paginator = Paginator(bookings, 10)
    page_number = request.GET.get("page")
    bookings_page = paginator.get_page(page_number)

    return render(request, "instructor/booking_detail.html", {
        "course": course,
        "bookings": bookings_page,
    })


@login_required
def instructor_video_order_detail(request,  order_id):

    orders = CourseOrder.objects.filter(course_name=order_id)

    return render(request, "instructor/video_order_detail.html", {
        "course": orders.first(),
        "orders": orders,
    })


@login_required
def user_booking_history(request):
    bookings = CourseBooking.objects.filter(user=request.user).order_by("-booking_date")
    video_orders = VideoCourseOrder.objects.filter(user=request.user).order_by("-payment_date")  # ✅ ใช้ payment_date แทน

    return render(request, "booking_history.html", {
        "bookings": bookings,
        "video_orders": video_orders,
    })


@login_required
def my_courses(request):
    # ดึงข้อมูลการจองคอร์ส
    bookings = CourseBooking.objects.filter(user=request.user).order_by("-booking_date")
    
    # ดึงข้อมูลคอร์สวิดีโอที่ผู้ใช้ซื้อ
    purchased_video_courses = VideoCourseOrder.objects.filter(user=request.user)
    
    return render(request, 'my_courses.html', {
        'bookings': bookings,
        'purchased_video_courses': purchased_video_courses
    })

@login_required
def booking_my_courses(request, course_id):
    """ แสดงรายละเอียดข้อมูลของคอร์สที่ผู้ใช้คนปัจจุบันจอง """
    course = get_object_or_404(Course, id=course_id)

    # ✅ ดึงข้อมูลการจองที่เป็นของ `request.user` เท่านั้น
    bookings = CourseBooking.objects.filter(course=course, user=request.user).order_by("-booking_date")

    # ✅ ถ้าผู้ใช้ไม่มีการจองคอร์สนี้เลย ให้แจ้งเตือนหรือแสดงเป็นหน้า error
    if not bookings.exists():
        return render(request, "error.html", {"message": "คุณไม่มีสิทธิ์ดูข้อมูลการจองนี้"})

    return render(request, "booking_my_courses.html", {
        "course": course,
        "bookings": bookings
    })





@login_required
def profile_admin(request):
    return render(request, 'admin/profile_admin.html', {'user': request.user, 'profile': request.user.profile})

@login_required
def update_profile_admin(request):
    if request.method == 'POST':
        user = request.user
        profile = user.profile

        user.username = request.POST.get('username', user.username)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()  # ✅ บันทึกการเปลี่ยนแปลง
            
        messages.success(request, "บันทึกข้อมูลเรียบร้อยแล้ว!")
        return redirect(reverse('profile_admin')) 
    
    return render(request, 'admin/update_profile_admin.html', {'user': request.user, 'profile': request.user.profile})

# ฟังก์ชันสร้าง PIN 6 หลัก
def generate_pin():
    return ''.join(random.choices(string.digits, k=6))

# ✅ 1. API ขอรหัส PIN รีเซ็ตรหัสผ่าน
def request_reset_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = User.objects.get(email=email)
            pin = generate_pin()
            
            # ✅ ตั้งค่าเวลาหมดอายุของ PIN (5 นาที)
            request.session["reset_pin"] = {
                "pin": pin,
                "expires_at": (timezone.now() + timedelta(minutes=5)).isoformat()  # ใช้ timezone.now()
            }
            request.session["reset_email"] = email

            # ✅ ส่งอีเมล PIN ให้ผู้ใช้
            send_mail(
                "รหัส PIN รีเซ็ตรหัสผ่าน",
                f"รหัส PIN ของคุณคือ {pin} (หมดอายุใน 5 นาที)",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return redirect("verify_reset_pin")
        except User.DoesNotExist:
            messages.error(request, "ไม่พบอีเมลนี้ในระบบ")
    
    return render(request, "reset_password_request.html")
from django.utils import timezone  # เพิ่มการ import timezone
# ✅ 2. หน้า "ยืนยันรหัส PIN"
def verify_reset_password(request):
    if request.method == "POST":
        entered_pin = "".join([
            request.POST.get("pin1", ""),
            request.POST.get("pin2", ""),
            request.POST.get("pin3", ""),
            request.POST.get("pin4", ""),
            request.POST.get("pin5", ""),
            request.POST.get("pin6", ""),
        ])
        
        session_data = request.session.get("reset_pin", {})

        if not session_data:
            messages.error(request, "รหัส PIN หมดอายุ กรุณาขอใหม่")
            return redirect("reset_password_request")  

        stored_pin = session_data.get("pin")
        expires_at = session_data.get("expires_at")

        # ✅ ตรวจสอบว่ารหัส PIN หมดอายุหรือยัง
        if expires_at and timezone.now() > timezone.datetime.fromisoformat(expires_at):
            del request.session["reset_pin"]
            messages.error(request, "รหัส PIN หมดอายุ กรุณาขอใหม่")
            return redirect("reset_password_request")

        # ✅ ตรวจสอบว่ารหัส PIN ตรงกันหรือไม่
        if entered_pin == stored_pin:
            return redirect("reset_password")  # ✅ ตรวจสอบว่า `name="reset_password"` ตรงกับ `urls.py`
        else:
            messages.error(request, "รหัส PIN ไม่ถูกต้อง กรุณาลองอีกครั้ง")

    return render(request, "reset_password_verify.html")

# ✅ ฟังก์ชันตรวจสอบความแข็งแกร่งของรหัสผ่าน
def is_valid_password(password):
    """✅ ตรวจสอบว่ารหัสผ่านแข็งแกร่งพอหรือไม่"""
    return (
        len(password) >= 8 and
        re.search(r"[0-9]", password)
    )

# ✅ 3. หน้า "ตั้งรหัสผ่านใหม่"
def reset_password(request):
    if request.method == "POST":
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        if new_password != confirm_password:
            messages.error(request, "รหัสผ่านไม่ตรงกัน")
            return render(request, "reset_password_form.html")

        if not is_valid_password(new_password):
            messages.error(request, "รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัว และประกอบด้วยตัวพิมพ์เล็ก, ตัวพิมพ์ใหญ่, และตัวเลข")
            return render(request, "reset_password_form.html")

        email = request.session.get("reset_email")
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # ✅ ลบข้อมูล PIN ออกจาก session หลังจากเปลี่ยนรหัสผ่านสำเร็จ
            request.session.pop("reset_pin", None)
            request.session.pop("reset_email", None)

            return render(request, "reset_password_form.html", {"success": True})  # ✅ ส่ง success=True ไปยัง Template
        except User.DoesNotExist:
            messages.error(request, "ไม่พบบัญชีผู้ใช้")

    return render(request, "reset_password_form.html")


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(CourseBooking, id=booking_id, user=request.user)

    # ✅ เช็คว่าสถานะต้องเป็น "pending" ถึงจะยกเลิกได้
    if booking.booking_status == "pending":
        booking.booking_status = "canceled"
        booking.save()
        messages.success(request, "✅ คุณได้ยกเลิกการจองคอร์สเรียบร้อยแล้ว")
    else:
        messages.error(request, "⚠ ไม่สามารถยกเลิกได้ เนื่องจากการจองนี้ได้รับการยืนยันแล้ว")

    return redirect("my_courses")


@login_required
@instructor_required
def close_course(request, course_id):
    """ ปิดรับสมัครคอร์ส """
    print(f"🔍 กำลังปิดรับสมัครของคอร์ส: {course_id}")

    try:
        # ใช้ course_id ที่ถูกต้องจาก myapp_coursebooking
        course = get_object_or_404(Course, id=course_id)

        print(f"🔍 ก่อนอัปเดต: {course.is_closed}")

        course.is_closed = True
        course.save()

        print(f"✅ หลังอัปเดต: {course.is_closed}")
        messages.success(request, "✅ สิ้นสุดการรับสมัครของคอร์สเรียบร้อยแล้ว")
    except Course.DoesNotExist:
        print("❌ ไม่พบคอร์ส")
        messages.error(request, "❌ ไม่พบคอร์สที่ต้องการปิดรับสมัคร")

    return redirect("reservation_courses")




@login_required
@instructor_required
def reopen_course(request, course_id):
    """ เปิดรับสมัครคอร์สอีกครั้ง """
    print(f"🔍 กำลังเปิดรับสมัครของคอร์ส: {course_id}")

    try:
        # ใช้ course_id ที่ถูกต้องจาก myapp_coursebooking
        course = get_object_or_404(Course, id=course_id)

        print(f"🔍 ก่อนอัปเดต: {course.is_closed}")

        course.is_closed = False
        course.save()

        print(f"✅ หลังอัปเดต: {course.is_closed}")
        messages.success(request, "✅ เปิดรับสมัครของคอร์สนี้อีกครั้งเรียบร้อยแล้ว")
    except Course.DoesNotExist:
        print("❌ ไม่พบคอร์ส")
        messages.error(request, "❌ ไม่พบคอร์สที่ต้องการเปิดรับสมัคร")

    return redirect("reservation_courses")
