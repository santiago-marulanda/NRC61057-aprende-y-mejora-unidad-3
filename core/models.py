from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower


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
    ano = models.PositiveIntegerField(verbose_name="año") 
    color = models.CharField(max_length=40)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    placa = models.CharField(
        max_length=10,
        unique=True,
        error_messages={
            "unique": "Ya existe un vehículo registrado con esa placa.",
        },
    )
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
        constraints = [
            models.UniqueConstraint(
                Lower("placa"),
                name="uniq_vehiculo_placa_ci",
            ),
        ]

    @staticmethod
    def normalizar_placa(placa):
        return (placa or "").strip().upper()

    def clean(self):
        super().clean()

        self.placa = self.normalizar_placa(self.placa)
        if not self.placa:
            return

        duplicado = Vehiculo.objects.filter(placa__iexact=self.placa)
        if self.pk:
            duplicado = duplicado.exclude(pk=self.pk)

        if duplicado.exists():
            raise ValidationError(
                {"placa": "Ya existe un vehículo registrado con esa placa."}
            )

    def save(self, *args, **kwargs):
        self.placa = self.normalizar_placa(self.placa)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo} ({self.ano})"
