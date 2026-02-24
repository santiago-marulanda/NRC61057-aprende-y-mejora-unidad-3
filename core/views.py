from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView

from .models import Vehiculo

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def dispatch(self, request, *args, **kwargs):
        # if already authenticated send directly to admin dashboard
        if request.user.is_authenticated:
            return redirect("/admin/")
        return super().dispatch(request, *args, **kwargs)


def home(request):
    vehiculos = Vehiculo.objects.filter(activo=True).order_by("-created_at")[:6]
    return render(request, "core/home.html", {"vehiculos": vehiculos})


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({"status": "ok", "database": "up"})
    except Exception:
        return JsonResponse({"status": "error", "database": "down"}, status=503)
