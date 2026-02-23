from django.conf import settings
from django.db import models


class Categoria(models.Model):
    """
    Categoría de vehículo (ej. Automóvil, Camioneta, Campero).
    Se asume que estas categorías pueden estar precargadas en la base de datos
    y luego ser consultadas desde la interfaz (requisito del proyecto).
    """
    nombre = models.CharField(max_length=60, unique=True) 
    descripcion = models.TextField(blank=True)     

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Vehiculo(models.Model):
    """
    Vehículo publicado para venta dentro del sistema.
    Incluye datos obligatorios del enunciado (marca, modelo, año, color, precio,
    placa única, categoría, estado, vendedor, observaciones e imagen).
    """

    class Estado(models.TextChoices):
        NUEVO = "NUEVO", "Nuevo"
        USADO = "USADO", "Usado"

    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=80)
    ano = models.PositiveIntegerField() 
    color = models.CharField(max_length=40)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    placa = models.CharField(max_length=10, unique=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,        
        related_name="vehiculos",
    )
    estado = models.CharField(max_length=5, choices=Estado.choices)
    activo = models.BooleanField(default=True)

    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,        
        on_delete=models.PROTECT,      
        related_name="vehiculos",
    )
    observaciones = models.TextField(blank=True)        
    imagen = models.ImageField(upload_to="vehiculos/", blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo} ({self.ano})"
