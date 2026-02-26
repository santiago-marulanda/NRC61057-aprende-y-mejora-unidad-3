from django.shortcuts import redirect

from core.roles import ROLE_COMPRADOR, get_active_role, get_user_roles


class RoleSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.available_roles = get_user_roles(request.user)
        request.active_role = get_active_role(request)
        return self.get_response(request)


class AdminRoleGuardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path.startswith("/admin/"):
            # Permitir logout para que el usuario pueda salir en cualquier rol.
            if request.path != "/admin/logout/":
                active_role = getattr(request, "active_role", None)
                if active_role == ROLE_COMPRADOR:
                    return redirect("/")
        return self.get_response(request)

