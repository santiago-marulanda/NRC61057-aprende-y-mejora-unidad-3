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
    # use a helper method for the year so Django doesn't apply
    # the locale-specific thousands separator (e.g. 2.026). Return
    # a string so template localization/number formatting is skipped.
    def ano_sin_separador(self, obj):
        return str(obj.ano)
    ano_sin_separador.short_description = "Año"
    ano_sin_separador.admin_order_field = "ano"

    list_display = (
        "placa",
        "marca",
        "modelo",
        "ano_sin_separador",
        "categoria",
        "estado",
        "precio",
        "vendedor",
        "activo",
        "created_at",
    )
    list_filter = ("categoria", "estado", "activo", "ano")  # filters still use raw field
    search_fields = ("placa", "marca", "modelo", "color", "vendedor__username", "vendedor__email")
    ordering = ("-created_at",)
    list_per_page = 25
    list_max_show_all = 200

    # Mejora la UX en admin para relaciones
    autocomplete_fields = ("categoria", "vendedor")

