from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                # Redirige a login si no está autenticado
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())

            if user.role in allowed_roles or user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Si el rol no está permitido, devuelve 403
            raise PermissionDenied("No tienes permiso para acceder a esta página.")
        return _wrapped_view
    return decorator
