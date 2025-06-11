from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile  # นำเข้า Model Profile
from .models import CourseDetails,Course, CourseBooking
from myapp.models import CourseBooking 
from django.utils.timezone import localtime
from .models import InstructorProfile
from .models import Banner
from django.conf import settings
from .models import VideoCourseOrder, VideoCourse

def get_booking_date(self, obj):
    if obj.booking_date:
        return localtime(obj.booking_date).strftime("%d %b %Y, %H:%M")
    return "ไม่ระบุวันที่"

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

#------------------------------------------------สำหรับapiเไฟล์นี้ใช้สำหรับแปลงข้อมูล User และ Profile เป็น JSON

# ✅ เพิ่ม Serializer สำหรับ Profile
class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)  # อนุญาตให้อัปโหลดรูปภาพได้

    class Meta:
        model = UserProfile
        fields = ['profile_picture']


# ✅ Serializer สำหรับข้อมูลโปรไฟล์ของผู้ใช้
class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()  # รวมข้อมูลจาก ProfileSerializer

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'profile']

class CourseDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDetails
        fields = '__all__' 

class AddCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__' 

class CourseBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseBooking
        fields = '__all__' 


# ✅ Serializer สำหรับข้อมูลคอร์ส
class CourseSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price','instructor', 'image_url']

    def get_image_url(self, obj):
        """ คืนค่า URL เต็มของรูปภาพ """
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if obj.image else None


# ✅ Serializer สำหรับข้อมูลการจองคอร์ส
class BookingDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email')
    course = CourseSerializer()  # ✅ ดึงข้อมูลคอร์สทั้งหมด

    class Meta:
        model = CourseBooking
        fields = [
            'id', 'course', 'user_email', 'student_name', 'student_name_en', 
            'nickname_th', 'nickname_en', 'age', 'grade', 'parent_nickname', 
            'phone', 'line_id', 'booking_status', 'payment_slip'
        ]




class BookingHistorySerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    booking_date = serializers.SerializerMethodField()
    selected_course = serializers.SerializerMethodField()
    booking_status_display = serializers.CharField(source="get_booking_status_display", read_only=True)
    payment_status_display = serializers.CharField(source="get_payment_status_display", read_only=True)
    payment_slip_url = serializers.SerializerMethodField()

    class Meta:
        model = CourseBooking
        fields = [
            "id", "course_title", "selected_course", "booking_date",
            "booking_status_display", "payment_status_display", "payment_slip_url"
        ]

    def get_booking_date(self, obj):
       if obj.booking_date:
           return localtime(obj.booking_date).strftime("%d %b %Y, %H:%M")
       return "ไม่ระบุวันที่"

    def get_selected_course(self, obj):
        return obj.get_selected_course_display()

    def get_payment_slip_url(self, obj):
        request = self.context.get('request')
        if obj.payment_slip:
            return request.build_absolute_uri(obj.payment_slip.url)
        return None

class InstructorProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()  # ทำให้ URL ของรูปถูกต้อง

    class Meta:
        model = InstructorProfile
        fields = ['id', 'name', 'email', 'expertise', 'profile_picture']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None  # ถ้าไม่มีรูปภาพ
    
class InstructorProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = InstructorProfile
        fields = ['id', 'full_name', 'email', 'phone', 'age', 'subject', 'profile_picture']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None
    

class BannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # ✅ ฟิลด์ใหม่สำหรับ URL เต็ม

    class Meta:
        model = Banner
        fields = ["id", "image_url", "created_at", "status", "rejection_message"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)  # ✅ ส่ง URL เต็ม
        return None
    
class CourseSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'instructor', 'created_at', 'status', 'image_url']

    

    def get_image_url(self, obj):
        """
        ✅ ใช้ URL เต็มสำหรับรูปภาพ
        """
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
    


class VideoCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoCourse
        fields = ['id', 'title', 'description', 'price', 'image', 'instructor']

class VideoCourseOrderSerializer(serializers.ModelSerializer):
    course = VideoCourseSerializer(read_only=True)  # ดึงข้อมูลคอร์สวิดีโอแบบเต็ม

    class Meta:
        model = VideoCourseOrder
        fields = ['id', 'user', 'course', 'payment_slip', 'payment_status', 'transaction_id', 'payment_date']