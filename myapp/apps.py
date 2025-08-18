from django.apps import AppConfig

class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"

    def ready(self):
        # สร้าง Group พื้นฐาน หากยังไม่มี (กันเคส DB เพิ่งตั้งใหม่)
        from django.contrib.auth.models import Group
        from django.db.utils import OperationalError, ProgrammingError
        try:
            for name in ["Admin", "Instructor", "Member"]:
                Group.objects.get_or_create(name=name)
        except (OperationalError, ProgrammingError):
            # ช่วง migrate ครั้งแรก ตารางอาจยังไม่พร้อม ให้ข้ามไป
            pass
