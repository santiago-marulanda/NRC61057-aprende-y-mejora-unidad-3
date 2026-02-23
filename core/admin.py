from django.contrib import admin
from .models import Categoria, Vehiculo


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # Configuración del panel admin para gestionar categorías
    list_display = ("nombre",)
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    # Configuración del panel admin para gestionar vehículos
    list_display = (
        "placa",
        "marca",
        "modelo",
        "ano",
        "categoria",
        "estado",
        "precio",
        "vendedor",
        "activo",
        "created_at",
    )
    list_filter = ("categoria", "estado", "activo", "ano")
    search_fields = ("placa", "marca", "modelo", "color", "vendedor__username", "vendedor__email")
    ordering = ("-created_at",)
    list_per_page = 25
    list_max_show_all = 200

    # Mejora la UX en admin para relaciones
    autocomplete_fields = ("categoria", "vendedor")

