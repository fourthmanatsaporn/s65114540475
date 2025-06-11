from django.urls import path
from . import views
from .views import register, login_view
from rest_framework_simplejwt.views import TokenRefreshView
from .views import youtube_video_details

urlpatterns = [
    # สำหรับ Web
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', views.home, name='home'),  # เพิ่มเส้นทาง root
    path('update_profile/', views.update_profile, name='update_profile'),
    path('check-password/', views.check_password, name='check_password'),
    path('verify-password/', views.verify_password, name='verify_password'),
    path('change-password/', views.change_password, name='change_password'),
    path('all-courses/', views.all_courses, name='all_courses'),
    path('user-list/', views.user_list, name='user_list'),  # ✅ ตรวจสอบเส้นทาง
    path('staff/add/<int:user_id>/', views.add_staff, name='add_staff'),  # ✅ เพิ่ม <int:user_id>
    path('contact/', views.contact, name='contact'),  # เพิ่ม path สำหรับหน้าติดต่อเรา
    path('instructor/', views.instructor_sales, name='instructor_sales'),
    path('ireservation/', views.reservation_courses, name='reservation_courses'),
    path('add_course/', views.add_course, name='add_course'),
    path('edit-course/<int:course_id>/', views.edit_course, name='edit_course'),

    path('video_course_details/<int:course_id>/', views.video_course_details, name='video_course_details'),
    path('video_courses/', views.video_courses, name='instructor_live_courses'),
    path('add_video_course/', views.add_video_course, name='add_video_course'),
    path('add_video_course_details/<int:course_id>/', views.add_video_course_details, name='add_video_course_details'), 
    path('edit_video_course/<int:course_id>/', views.edit_video_course, name='edit_video_course'),
    path('edit_video_course_details/<int:course_id>/', views.edit_video_course_details, name='edit_video_course_details'),
    path('edit_video_lesson/<int:course_id>/', views.edit_video_lesson, name='edit_video_lesson'),
    path('approve_video_course/<int:course_id>/', views.approve_video_course, name="approve_video_course"),
    path('send_back_video_course/<int:course_id>/', views.send_back_video_course, name="send_back_video_course"),
    path('upload_video_course_qr/<int:course_id>/', views.upload_video_course_qr, name='upload_video_course_qr'),
    path('video_course_details_user/<int:course_id>/', views.video_course_details_user, name='video_course_details_user'),
    path('purchase_video_course/<int:course_id>/', views.purchase_video_course, name='purchase_video_course'),
    path('confirm-video-order/<int:order_id>/', views.confirm_video_order, name='confirm_video_order'),
    path('reject-video-order/<int:order_id>/', views.reject_video_order, name='reject_video_order'),
    path('video-lesson-view/<int:course_id>/', views.video_lesson_view, name='video_lesson_view'),
    path('video_order_detail_instructor/<int:course_id>/', views.video_order_detail_instructor, name='video_order_detail_instructor'),
    path('delete_selected_video_courses/', views.delete_selected_video_courses, name='delete_selected_video_courses'),




    


    path('add_course_details/<int:course_id>/', views.add_course_details, name='add_course_details'),
    path('edit-course-details/<int:course_id>/', views.edit_course_details, name='edit_course_details'),
    path('submit_course_for_review/<int:course_id>/', views.submit_course_for_review, name='submit_course_for_review'),
    path('banners/', views.banners, name='banners'),
    path('add_banner/', views.add_banner, name='add_banner'),
    path('delete_banner/<int:banner_id>/', views.delete_banner, name='delete_banner'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('review_booking_courses/', views.review_booking_courses, name='review_booking_courses'),
    path('approve_course/<int:course_id>/', views.approve_course, name='approve_course'),
    path('send-back-course/<int:course_id>/', views.send_back_course, name='send_back_course'),
    path('upload_payment_qr/<int:course_id>/', views.upload_payment_qr, name='upload_payment_qr'),
    path('sales/', views.sales, name='sales'),
    path('user-list/', views.user_list, name='user_list'),
    path('delete-selected-courses/', views.delete_selected_courses, name='delete_selected_courses'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('instructor/logout/', views.instructor_logout, name='instructor_logout'),  # Logout สำหรับ Instructor
    path('admin_logout/', views.admin_logout, name='admin_logout'), 
    path('courses/<int:course_id>/', views.course_details, name='course_details'),
    path('register-instructor/', views.register_instructor, name='register_instructor'),
    path('staff/', views.instructor_list, name='instructor_list'),
    path('admin_banners/', views.banners_admin, name='banners_admin'),
    path('approve_banner/<int:banner_id>/', views.approve_banner, name='approve_banner'),
    path('reject_banner/<int:banner_id>/', views.reject_banner, name='reject_banner'),
    path('course_details_admin/<int:course_id>/', views.course_details_admin, name='course_details_admin'),
    path('booking/<int:course_id>/', views.booking_course, name='booking_course'),
    path("submit-booking/<int:course_details_id>/", views.submit_booking, name="submit_booking"),
    path("payment/<int:booking_id>/", views.payment_page, name="payment_page"),
    path("submit-payment/<int:booking_id>/", views.submit_payment, name="submit_payment"),
    path("sales/booking/<int:course_id>/", views.booking_detail, name="booking_detail"),
    path("sales/video/<int:order_id>/", views.video_order_detail, name="video_order_detail"),
    path("instructor/sales/", views.instructor_sales, name="instructor_sales"),
    path("instructor/booking/<int:course_id>/", views.instructor_booking_detail, name="instructor_booking_detail"),
    path("instructor/video/<int:order_id>/", views.instructor_video_order_detail, name="instructor_video_order_detail"),
    path("booking-history/", views.user_booking_history, name="booking_history"),
    path('my-courses/', views.my_courses, name='my_courses'),  # คอร์สเรียนของฉัน
    path('booking-my-courses/<int:course_id>/', views.booking_my_courses, name='booking_my_courses'), 
    path('profile-instructor/', views.profile_instructor, name='profile_instructor'), 
    path('update-profile-instructor/', views.update_profile_instructor, name='update_profile_instructor'), 
    path('profile-admin/', views.profile_admin, name='profile_admin'), 
    path('update-profile-admin/', views.update_profile_admin, name='update_profile_admin'), 
    path('reset-password/', views.request_reset_password, name='reset_password_request'),
    path('verify-reset-pin/', views.verify_reset_password, name='verify_reset_pin'),
    path('set-new-password/', views.reset_password, name='reset_password'),
    path("update-booking-status/<int:booking_id>/<str:status>/", views.update_booking_status, name="update_booking_status"),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('close-course/<int:course_id>/', views.close_course, name='close_course'),
    path('reopen-course/<int:course_id>/', views.reopen_course, name='reopen_course'),

#---------------------------ทดสอบAPi
    path("youtube/", youtube_video_details, name="youtube_video_details"),
    path('add_video_lesson/<int:course_id>/', views.add_video_lesson, name='add_video_lesson'),
    path("review_video_courses/", views.review_video_courses, name="review_video_courses"),  # ✅ เพิ่มเส้นทางนี้

    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # สำหรับ API
    path('api/register/', views.register_api, name='register_api'),
    path('api/login/', views.login_api, name='login_api'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # สำหรับ Refresh Token
    path('api/user/', views.get_user_data, name='get_user_data'),
    path('api/approved-courses/', views.get_approved_courses, name='get_approved_courses'),
    path('api/banners/', views.banners_api, name='banners_api'),  # API สำหรับดึงแบนเนอร์
    path('api/staffs/', views.staff_list_api, name='staff_list_api'),
    path('api/profile/', views.profile_api, name='profile_api'),
    path('api/profile/update/', views.update_profile_api, name='update_profile_api'),
    path('api/course/<int:course_id>/', views.course_details_api, name='course_details_api'),
    path("api/book-course/<int:course_id>/", views.api_submit_booking, name="api_submit_booking"),
    path("api/payment-details/<int:booking_id>/", views.api_payment_details, name="api_payment_details"),
    path("api/submit-payment/<int:booking_id>/", views.api_submit_payment, name="api_submit_payment"),
    path("api/booking-status/<int:booking_id>/", views.api_booking_status, name="api_booking_status"),
    path("api/my-bookings/", views.api_user_bookings, name="api_user_bookings"),
    path('api/my-courses/', views.my_courses_api, name='my_courses_api'),
    path('api/booking-my-courses/<int:course_id>/', views.booking_my_courses_api, name='booking_my_courses_api'),
    path('api/user-booking-history/',views.user_booking_history_api, name='user_booking_history_api'),
    path('api/instructors/', views.instructor_list_api, name='instructor_list_api'),
    path('api/verify-password/', views.verify_password_api, name='verify_password_api'),
    path('api/change-password/', views.change_password_api, name='change_password_api'),
    path('api/instructor-profile/', views.instructor_profile_api, name='instructor_profile_api'),
    path('api/update-instructor-profile/', views.update_instructor_profile_api, name='update_instructor_profile_api'),
    path('api/profile-admin/', views.profile_admin_api, name='profile_admin_api'),
    path('api/update-profile-admin/', views.update_profile_admin_api, name='update_profile_admin_api'),
    path('api/instructor-sales/', views.instructor_sales_api, name='instructor_sales_api'),
    path('api/instructor-booking-detail/<int:course_id>/', views.instructor_booking_detail_api, name='instructor_booking_detail_api'),
    path('api/banners_list/', views.list_banners_api, name="list_banners_api"),
    path('api/banners/add/', views.add_banner_api, name="add_banner_api"),
    path('api/banners/pending/', views.list_pending_banners_api, name="list_pending_banners_api"),
    path('api/banners/<int:banner_id>/approve/', views.approve_banner_api, name="approve_banner_api"),
    path('api/banners/<int:banner_id>/reject/', views.reject_banner_api, name="reject_banner_api"),
    path('api/banners/<int:banner_id>/delete/', views.delete_banner_api, name="delete_banner_api"),
        # ✅ API สำหรับเพิ่มคอร์สใหม่
    path('api/add-course/', views.add_course_api, name='add_course_api'),
    path('api/add-course-details/<int:course_id>/', views.add_course_details_api, name='add_course_details_api'),


    # ✅ API สำหรับดึงรายการคอร์สทั้งหมดของ Instructor
    path('api/list_reservation_courses_api/', views.list_reservation_courses_api, name='list_reservation_courses_api'),

    # ✅ API สำหรับแก้ไขคอร์ส
    path('api/edit-course/<int:course_id>/', views.edit_course_api, name='edit_course_api'),
    path('api/edit-course-details-api/<int:course_id>/', views.edit_course_details_api, name='edit_course_details_api'),
    path("api/get-course/<int:course_id>/", views.get_course_api, name="get_course_api"),
    path('api/get-course-details/<int:course_id>/', views.get_course_details_api, name='get_course_details_api'),

    # ✅ API สำหรับส่งคอร์สให้แอดมินตรวจสอบ
    path('api/submit-course-review/<int:course_id>/', views.submit_course_review_api, name='submit_course_review_api'),
    path('api/delete-course/<int:course_id>/', views.delete_course_api, name='delete_course_api'),



    path('api/close-course/<int:course_id>/', views.close_course_api, name='close_course_api'),
    path('api/reopen-course/<int:course_id>/', views.reopen_course_api, name='reopen_course_api'),

    path("api/sales/", views.sales_api, name="sales_api"), 
    path("api/Admin-booking-detail-api/<int:course_id>/", views.Admin_booking_detail_api, name="Admin_booking_detail_api"), 
    path("api/users/", views.user_list_api, name="user_list_api"),
    path('api/register-instructor/', views.register_instructor_api, name='register-instructor-api'),
    path("api/banners_pending/", views.banners_admin_api, name="banners_admin_api"),
    path("api/Admin_banners/approve/<int:banner_id>/", views.Admin_approve_banner_api, name="approve_banner_api"),
    path("api/Admin_banners/reject/<int:banner_id>/", views.Admin_reject_banner_api, name="reject_banner_api"),
    path("api/review_booking_courses/", views.api_review_booking_courses, name="api_review_booking_courses"),
    path("api/approve_course/<int:course_id>/", views.api_approve_course, name="api_approve_course"),
    path("api/send_back_course/<int:course_id>/", views.api_send_back_course, name="api_send_back_course"),
    path("api/upload_payment_qr/<int:course_id>/", views.api_upload_payment_qr, name="api_upload_payment_qr"),
    path("api/booking/<int:booking_id>/update-status/", views.update_booking_status_api, name="update_booking_status_api"),
        # ✅ API รายได้รวม (สำหรับ Mobile)
    path("api/admin/dashboard/", views.admin_dashboard_api, name="admin_dashboard_api"),

    # ✅ API รายได้แยกตามคอร์ส
    path("api/admin/course-revenue/", views.course_revenue_api, name="course_revenue_api"),

    # ✅ API รายได้แยกตามเดือน
    path("api/admin/monthly-income/", views.monthly_income_api, name="monthly_income_api"),
    path("api/request-reset-password/", views.request_reset_password_api, name="request_reset_password_api"),
    path("api/verify-reset-password/", views.verify_reset_password_api, name="verify_reset_password_api"),
    path("api/reset-password/", views.reset_password_api, name="reset_password_api"),
    path('api/video-course/<int:course_id>/', views.get_video_course_details, name='get_video_course_details'),
    path('api/video-lesson-view/<int:course_id>/', views.get_video_lessons, name='get_video_lessons'),
    path("api/purchase-video-course-api/<int:course_id>/", views.purchase_video_course_api, name="purchase_video_course_api"),
    path("api/video-order-detail-instructor/<int:course_id>/", views.video_order_detail_instructor_api, name="video_order_detail_instructor_api"),
    path("api/video-courses/", views.video_courses_api, name="video_courses_api"),

    path("api/add-video-course/", views.add_video_course_api, name="add_video_course_api"),
    path("api/add-video-course-details/<int:course_id>/", views.add_video_course_details_api, name="add_video_course_details_api"),
    path("api/add-video-lesson/<int:course_id>/", views.add_video_lesson_api, name="add_video_lesson_api"),

        # ✅ ดึงรายการคอร์สที่รอตรวจสอบ
    path("api/review-video-courses/", views.review_video_courses_api, name="review_video_courses_api"),

    # ✅ อนุมัติคอร์สเรียนแบบวิดีโอ
    path("api/approve-video-course/<int:course_id>/", views.approve_video_course_api, name="approve_video_course_api"),

    # ✅ ส่งคอร์สกลับไปแก้ไข
    path("api/send-back-video-course/<int:course_id>/", views.send_back_video_course_api, name="send_back_video_course_api"),

    # ✅ อัปโหลด QR Code สำหรับชำระเงิน
    path("api/upload-video-course-qr/<int:course_id>/", views.upload_video_course_qr_api, name="upload_video_course_qr_api"),

    # ดึงข้อมูลคำสั่งซื้อคอร์สเรียนแบบวิดีโอ
    path('api/video-order-detail/<int:course_id>/', views.video_order_detail_api, name='video_order_detail_api'),
    
    # อนุมัติการชำระเงิน
    path('api/confirm-video-order-api/<int:order_id>/', views.confirm_video_order_api, name='confirm_video_order_api'),
    
    # ปฏิเสธการชำระเงิน
    path('api/reject-video-order/<int:order_id>/', views.reject_video_order_api, name='reject_video_order'),

    path('api/delete-video-course/<int:course_id>/', views.delete_video_course_api, name='delete_video_course_api'),

        # ✅ API แก้ไขข้อมูลหลักของคอร์สวิดีโอ
    path('api/edit-video-course/<int:course_id>/', views.api_edit_video_course, name='api_edit_video_course'),

    # ✅ API แก้ไขรายละเอียดของคอร์สวิดีโอ
    path('api/edit-video-course-details/<int:course_id>/', views.api_edit_video_course_details, name='api_edit_video_course_details'),

    # ✅ API แก้ไขบทเรียนวิดีโอ
    path('api/edit-video-lesson-api/<int:course_id>/', views.api_edit_video_lesson, name='api_edit_video_lesson'),





    path('api/get-video-course_api/<int:course_id>/', views.get_video_course_api, name='get_video_course_api'),

    path('api/get-video-course-details/<int:course_id>/', views.get_video_course_details_api, name='get_video_course_details_api'),

    # urls.py
    path('api/get-video-lesson/<int:course_id>/', views.get_video_lesson_api, name='get_video_lesson_api'),















]





