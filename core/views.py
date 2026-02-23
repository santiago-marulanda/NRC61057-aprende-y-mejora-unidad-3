from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({"status": "ok", "database": "up"})
    except Exception:
        return JsonResponse({"status": "error", "database": "down"}, status=503)
