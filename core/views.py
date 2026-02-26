from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .models import Vehiculo
from .roles import ROLE_COMPRADOR, ROLE_VENDEDOR, get_active_role, get_user_roles

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def dispatch(self, request, *args, **kwargs):
        # If already authenticated, redirect according to active role.
        if request.user.is_authenticated:
            rol_activo = get_active_role(request)
            return redirect("/admin/" if rol_activo == ROLE_VENDEDOR else "/")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        rol_activo = get_active_role(self.request)
        next_url = self.get_redirect_url()

        # Compradores nunca deben entrar al admin.
        if rol_activo == ROLE_COMPRADOR:
            if next_url and not next_url.startswith("/admin/"):
                return next_url
            return "/"

        # Vendedor: respeta next si existe; si no, panel admin.
        if rol_activo == ROLE_VENDEDOR:
            return next_url or "/admin/"

        return next_url or "/"


def home(request):
    vehiculos = Vehiculo.objects.filter(activo=True).order_by("-created_at")[:6]
    return render(
        request,
        "core/home.html",
        {
            "vehiculos": vehiculos,
            "roles_disponibles": getattr(request, "available_roles", []),
            "rol_activo": getattr(request, "active_role", None),
        },
    )


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({"status": "ok", "database": "up"})
    except Exception:
        return JsonResponse({"status": "error", "database": "down"}, status=503)


@require_http_methods(["GET", "POST"])
@login_required
def cambiar_rol(request):
    if request.method == "POST":
        nuevo_rol = request.POST.get("rol")
        next_url = request.POST.get("next")
    else:
        nuevo_rol = request.GET.get("rol")
        next_url = request.GET.get("next")

    roles_disponibles = get_user_roles(request.user)

    if nuevo_rol in roles_disponibles:
        request.session["rol_activo"] = nuevo_rol

    # For links coming from Jazzmin user menu, fall back to the previous page.
    next_url = next_url or request.META.get("HTTP_REFERER") or "/"

    # Si cambia a comprador y viene de admin, redirigir al home.
    if nuevo_rol == ROLE_COMPRADOR and next_url.startswith("/admin/"):
        return redirect("/")

    # Si cambia a vendedor y estaba en home, facilitar entrada al panel.
    if nuevo_rol == ROLE_VENDEDOR and next_url == "/":
        return redirect("/admin/")

    return redirect(next_url)
