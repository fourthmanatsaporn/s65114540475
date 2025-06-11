from rest_framework.permissions import BasePermission

class IsInstructor(BasePermission):
    def has_permission(self, request, view=None):  # กำหนด view=None เป็นค่าเริ่มต้น
        return request.user.is_authenticated and request.user.groups.filter(name='Instructor').exists()

class IsAdmin(BasePermission):
    def has_permission(self, request, view=None):  # กำหนด view=None เป็นค่าเริ่มต้น
        return request.user.is_authenticated and request.user.groups.filter(name='Admin').exists()
