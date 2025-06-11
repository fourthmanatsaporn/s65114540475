from django.db import models
from django.contrib.auth.models import User, Group
import hashlib
from django.dispatch import receiver
from django.db.models.signals import post_save

class Course(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอการอนุมัติ'),
        ('approved', 'อนุมัติแล้ว'),
         ('revision', 'ส่งกลับมาแก้ไข'),
         ('revised', 'แก้ไขแล้วรอการตรวจสอบ'),
    ]
   
    is_closed = models.BooleanField(default=False, null=False) 
    title = models.CharField(max_length=200,unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='courses/images/')
    instructor = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    revision_message = models.TextField(blank=True, null=True)  # เพิ่มฟิลด์นี้
    created_at = models.DateTimeField(auto_now_add=True) 
    payment_qr = models.ImageField(upload_to='payment_qrs/', blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.title
    
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) 
    name = models.CharField(max_length=100)  # ชื่อที่ใช้แสดง
    subject = models.CharField(max_length=200)  # วิชาที่สอน
    image = models.ImageField(upload_to="staff_images/", blank=True, null=True)  # อัปโหลดรูปภาพ
    created_at = models.DateTimeField(auto_now_add=True)  # วันเวลาที่เพิ่ม

    def __str__(self):
        return self.name
    

class VideoCourse(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอการอนุมัติ'),
        ('approved', 'อนุมัติแล้ว'),
        ('revision', 'ส่งกลับไปแก้ไข'),
        ('revised', 'แก้ไขแล้วรอการตรวจสอบ'),
    ]

    title = models.CharField(max_length=255, unique=True, default="ไม่มีชื่อคอร์ส")
    description = models.TextField(verbose_name="คำอธิบาย")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคา")
    image = models.ImageField(upload_to='video_courses/images/', default='default_course_image.jpg')
    instructor = models.CharField(max_length=255, default="ไม่ระบุผู้สอน")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะ")
    revision_message = models.TextField(blank=True, null=True, verbose_name="ข้อความการแก้ไข")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สร้าง")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_closed = models.BooleanField(default=False, null=False) 
    payment_qr = models.ImageField(upload_to='videocourses/payment_qrs/', blank=True, null=True, verbose_name="QR Code การชำระเงิน")

    def __str__(self):
        return self.title


class CourseDetails(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    additional_description = models.TextField()
    image = models.ImageField(upload_to='course_images/')
    additional_image = models.ImageField(upload_to='course_additional_images/')
    extra_image_1 = models.ImageField(upload_to='course_extra_images/', null=True, blank=True)  # รูปภาพเพิ่มเติม 1
    extra_image_2 = models.ImageField(upload_to='course_extra_images/', null=True, blank=True)  # รูปภาพเพิ่มเติม 2
    created_at = models.DateTimeField(auto_now_add=True)


class VideoCourseDetails(models.Model):
    course = models.ForeignKey(VideoCourse, on_delete=models.CASCADE, related_name="details", verbose_name="คอร์สที่เกี่ยวข้อง")
    name = models.CharField(max_length=255, verbose_name="หัวข้อรายละเอียด")
    description = models.TextField(verbose_name="คำอธิบาย")
    additional_description = models.TextField(verbose_name="รายละเอียดเพิ่มเติม")
    image = models.ImageField(upload_to='videocourse_details/images/', verbose_name="รูปภาพหลักของรายละเอียด")
    additional_image = models.ImageField(upload_to='videocourse_details/extra_images/', verbose_name="รูปภาพเพิ่มเติม 1", blank=True, null=True)
    preview_video = models.FileField(upload_to='videocourse_details/previews/', verbose_name="วิดีโอตัวอย่าง", blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สร้าง")

    def __str__(self):
        return f"{self.course.title} - {self.name}"

    

class Banner(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รออนุมัติ'),
        ('approved', 'อนุมัติแล้ว'),
        ('rejected', 'ไม่อนุมัติ'),
    ]

    instructor = models.ForeignKey(User, on_delete=models.CASCADE,  verbose_name="ผู้สอน", null=True, blank=True)
    image = models.ImageField(upload_to='banners/', verbose_name="รูปภาพ")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะ")
    rejection_message = models.TextField(blank=True, null=True, verbose_name="เหตุผลการไม่อนุมัติ")

    def __str__(self):
        return f"Banner {self.id} - {self.get_status_display()} by {self.instructor.username}"
    
    


    

class VideoLesson(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอการตรวจสอบ'),
        ('approved', 'อนุมัติแล้ว'),
        ('revision', 'ส่งกลับไปแก้ไข'),
    ]

    course = models.ForeignKey(VideoCourse, on_delete=models.CASCADE, null=True, blank=True)  
    title = models.CharField(max_length=255, default="ไม่มีชื่อบทเรียน", verbose_name="ชื่อวิดีโอ")
    description = models.TextField(verbose_name="คำอธิบาย")
    google_drive_id = models.CharField(max_length=100, verbose_name="Google Drive File ID", default="", blank=True)
    duration = models.CharField(max_length=50, verbose_name="ระยะเวลา")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ผู้สอน")
    is_approved = models.BooleanField(default=False, verbose_name="ตรวจสอบแล้ว")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="สถานะ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สร้าง")

    document = models.FileField(upload_to='lesson_documents/', blank=True, null=True, verbose_name="เอกสารประกอบการเรียน")


    def __str__(self):
        return f"{self.course.title} - {self.title}"



class CourseOrder(models.Model):
    course_name = models.CharField(max_length=255, verbose_name="ชื่อคอร์ส")
    customer_name = models.CharField(max_length=255, verbose_name="ชื่อลูกค้า")
    email = models.EmailField(verbose_name="อีเมลลูกค้า")
    transfer_slip = models.ImageField(upload_to='transfer_slips/', verbose_name="สลิปการโอน")
    status = models.CharField(max_length=50, choices=[('paid', 'จ่ายแล้ว'), ('pending', 'รอการตรวจสอบ')], default='pending', verbose_name="สถานะ")
    order_date = models.DateField(auto_now_add=True, verbose_name="เวลาการจอง")

    def __str__(self):
        return f"{self.customer_name} - {self.course_name}"
    

class VideoCourseOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ผู้ซื้อ")
    course = models.ForeignKey('VideoCourse', on_delete=models.CASCADE, verbose_name="คอร์สที่ซื้อ")
    payment_slip = models.ImageField(upload_to='payment_slips/', verbose_name="สลิปการโอนเงิน")
    payment_status = models.CharField(
        max_length=10,
        choices=[('pending', 'รออนุมัติ'), ('confirmed', 'ชำระแล้ว'), ('rejected', 'ปฏิเสธ')],
        default='pending',
        verbose_name="สถานะการชำระเงิน"
    )
    transaction_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="เลขที่รายการโอนเงิน")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="วันที่ชำระเงิน")

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.payment_status}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile" ,default=1)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)  
    role = models.CharField(max_length=20, choices=[('member', 'Member'), ('teacher', 'Teacher')])

    def get_profile_picture(self):
        """✅ ใช้รูปที่อัปโหลด ถ้าไม่มีให้ใช้ค่าเริ่มต้น"""
        if self.profile_picture:
            return self.profile_picture.url
        return "/static/images/PF.png" 

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance, 
            first_name=instance.first_name, 
            last_name=instance.last_name, 
            email=instance.email
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


    

class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="instructor_profile")
    profile_picture = models.ImageField(upload_to="instructors/profile_pictures/", blank=True, null=True)
    phone = models.CharField(max_length=20)
    age = models.PositiveIntegerField()
    subject = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # ตรวจสอบว่าผู้ใช้ยังไม่มีอยู่ในกลุ่ม Instructor
        instructor_group, created = Group.objects.get_or_create(name="Instructor")
        if not self.user.groups.filter(name="Instructor").exists():
            self.user.groups.add(instructor_group)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.subject}"
    

class CourseBooking(models.Model):
    # ✅ ข้อมูลนักเรียน
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    student_name = models.CharField(max_length=255)  # ชื่อจริง-นามสกุล (ภาษาไทย)
    student_name_en = models.CharField(max_length=255)  # ชื่อจริง-นามสกุล (ภาษาอังกฤษ)
    nickname_th = models.CharField(max_length=50)  # ชื่อเล่น (ไทย)
    nickname_en = models.CharField(max_length=50)  # ชื่อเล่น (อังกฤษ)
    age = models.IntegerField()
    grade = models.CharField(
        max_length=30,
        choices=[
            ("อนุบาล 2", "อนุบาล 2"),
            ("อนุบาล 3", "อนุบาล 3"),
            ("ประถมศึกษาปีที่ 1", "ประถมศึกษาปีที่ 1"),
            ("ประถมศึกษาปีที่ 2", "ประถมศึกษาปีที่ 2"),
            ("ประถมศึกษาปีที่ 3", "ประถมศึกษาปีที่ 3"),
            ("ประถมศึกษาปีที่ 4", "ประถมศึกษาปีที่ 4"),
            ("ประถมศึกษาปีที่ 5", "ประถมศึกษาปีที่ 5"),
            ("ประถมศึกษาปีที่ 6", "ประถมศึกษาปีที่ 6"),
            ("อื่นๆ", "อื่นๆ"),
        ]
    )
    other_grade = models.CharField(max_length=255, blank=True, null=True)

    # ✅ ข้อมูลผู้ปกครอง
    parent_nickname = models.CharField(max_length=50)  # ชื่อเล่นผู้ปกครอง
    phone = models.CharField(max_length=15)
    line_id = models.CharField(max_length=100, blank=True, null=True)  # ไอดีไลน์

    # ✅ รายละเอียดคอร์ส
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # ✅ เปลี่ยนเป็น ForeignKey

    selected_course = models.CharField(
        max_length=50,
        choices=[
            ("K1", "K1 = 9:00 - 10:00"),
            ("K2-3", "K2-3 = 10:30 - 11:30"),
            ("P1-3", "P1-3 = 10:30 - 11:30"),
            ("P4-6", "P4-6 = 10:30 - 11:30"),
        ],
        default="K1"
    )


    # ✅ การชำระเงิน
    payment_slip = models.ImageField(upload_to='payment_slips/', blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "รอการตรวจสอบ"),
            ("approved", "ชำระแล้ว"),
            ("rejected", "ปฏิเสธ"),
        ],
        default="pending"
    )

    # ✅ สถานะการจอง
    booking_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "รอการยืนยัน"),
            ("confirmed", "จองสำเร็จ"),
            ("canceled", "จองไม่สำเร็จ"),
        ],
        default="pending"
    )

    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.course}"
    

