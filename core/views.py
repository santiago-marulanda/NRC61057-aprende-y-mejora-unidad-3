import re

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from .models import Categoria, Vehiculo
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


def catalogo(request):
    categoria = request.GET.get("categoria", "").strip()
    estado = request.GET.get("estado", "").strip().upper()
    marca = request.GET.get("marca", "").strip()
    orden = request.GET.get("orden", "recientes")
    page_number = request.GET.get("page", "1")

    vehiculos = Vehiculo.objects.filter(activo=True).select_related("categoria", "vendedor")

    categorias = Categoria.objects.order_by("nombre")
    marcas = (
        Vehiculo.objects.filter(activo=True)
        .order_by("marca")
        .values_list("marca", flat=True)
        .distinct()
    )

    if categoria:
        categoria_normalizada = ""
        if re.fullmatch(r"[\d\s\.,]+", categoria):
            categoria_normalizada = re.sub(r"[^\d]", "", categoria)

        if categoria_normalizada:
            categoria = categoria_normalizada
            vehiculos = vehiculos.filter(categoria_id=int(categoria_normalizada))
        else:
            vehiculos = vehiculos.filter(categoria__nombre__iexact=categoria)

    if estado in {Vehiculo.Estado.NUEVO, Vehiculo.Estado.USADO}:
        vehiculos = vehiculos.filter(estado=estado)
    else:
        estado = ""

    if marca:
        vehiculos = vehiculos.filter(marca=marca)

    opciones_orden = {
        "recientes": "-created_at",
        "precio_asc": "precio",
        "precio_desc": "-precio",
    }
    orden = orden if orden in opciones_orden else "recientes"

    vehiculos = vehiculos.order_by(opciones_orden[orden], "-created_at")
    paginator = Paginator(vehiculos, 20)
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    query_params.pop("page", None)
    filtros_sin_pagina = query_params.urlencode()

    return render(
        request,
        "core/catalogo.html",
        {
            "vehiculos": page_obj.object_list,
            "page_obj": page_obj,
            "categorias": categorias,
            "marcas": marcas,
            "filtros": {
                "categoria": categoria,
                "estado": estado,
                "marca": marca,
                "orden": orden,
            },
            "filtros_sin_pagina": filtros_sin_pagina,
            "total_resultados": paginator.count,
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
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = "/"

    # Si cambia a comprador y viene de admin, redirigir al home.
    if nuevo_rol == ROLE_COMPRADOR and next_url.startswith("/admin/"):
        return redirect("/")

    # Si cambia a vendedor (staff), llevar siempre al panel de administración.
    if nuevo_rol == ROLE_VENDEDOR and request.user.is_staff:
        return redirect("/admin/")

    return redirect(next_url)
