from django.http import HttpResponseForbidden
from functools import wraps


def role_required(required_role):
    """
    Decorator ตรวจสอบ role ของผู้ใช้
    ใช้กับ view เช่น:
        @role_required('driver')
        def driver_jobs(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("กรุณาเข้าสู่ระบบ")
            profile = getattr(request.user, "customerprofile", None)
            if not profile or profile.role != required_role:
                return HttpResponseForbidden("สิทธิ์ไม่เพียงพอ")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
