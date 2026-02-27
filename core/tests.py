from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Vehiculo


class CatalogoViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.vendedor = user_model.objects.create_user(
            username="vendedor_rf3",
            password="123456",
            first_name="Laura",
            last_name="Luna",
            email="laura@example.com",
        )

        self.cat_auto = Categoria.objects.create(id=2101, nombre="Automóvil")
        self.cat_suv = Categoria.objects.create(id=2102, nombre="SUV")

        self.v1 = Vehiculo.objects.create(
            marca="Kia",
            modelo="Picanto",
            ano=2021,
            color="Rojo",
            precio="50000000.00",
            placa="AAA111",
            categoria=self.cat_auto,
            estado=Vehiculo.Estado.USADO,
            activo=True,
            vendedor=self.vendedor,
        )
        self.v2 = Vehiculo.objects.create(
            marca="Mazda",
            modelo="CX5",
            ano=2020,
            color="Azul",
            precio="120000000.00",
            placa="BBB222",
            categoria=self.cat_suv,
            estado=Vehiculo.Estado.USADO,
            activo=True,
            vendedor=self.vendedor,
        )
        self.v3_inactivo = Vehiculo.objects.create(
            marca="Renault",
            modelo="Logan",
            ano=2019,
            color="Gris",
            precio="45000000.00",
            placa="CCC333",
            categoria=self.cat_auto,
            estado=Vehiculo.Estado.USADO,
            activo=False,
            vendedor=self.vendedor,
        )

    def test_catalogo_muestra_solo_activos(self):
        response = self.client.get(reverse("catalogo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kia Picanto")
        self.assertContains(response, "Mazda CX5")
        self.assertNotContains(response, "Renault Logan")
        self.assertContains(response, "Laura Luna")
        self.assertContains(response, "laura@example.com")

    def test_catalogo_filtra_por_categoria(self):
        response = self.client.get(
            reverse("catalogo"),
            {"categoria": str(self.cat_suv.id)},
        )

        self.assertEqual(response.status_code, 200)
        vehiculos = list(response.context["vehiculos"])
        self.assertEqual([vehiculo.pk for vehiculo in vehiculos], [self.v2.pk])

    def test_catalogo_filtra_por_nombre_categoria(self):
        response = self.client.get(
            reverse("catalogo"),
            {"categoria": "automóvil"},
        )

        self.assertEqual(response.status_code, 200)
        vehiculos = list(response.context["vehiculos"])
        self.assertEqual([vehiculo.pk for vehiculo in vehiculos], [self.v1.pk])

    def test_catalogo_filtra_por_categoria_con_formato_localizado(self):
        response = self.client.get(
            reverse("catalogo"),
            {"categoria": "2.102"},
        )

        self.assertEqual(response.status_code, 200)
        vehiculos = list(response.context["vehiculos"])
        self.assertEqual([vehiculo.pk for vehiculo in vehiculos], [self.v2.pk])

    def test_catalogo_ordena_por_precio(self):
        response = self.client.get(reverse("catalogo"), {"orden": "precio_asc"})
        vehiculos_asc = [vehiculo.pk for vehiculo in response.context["vehiculos"]]
        self.assertEqual(vehiculos_asc, [self.v1.pk, self.v2.pk])

        response = self.client.get(reverse("catalogo"), {"orden": "precio_desc"})
        vehiculos_desc = [vehiculo.pk for vehiculo in response.context["vehiculos"]]
        self.assertEqual(vehiculos_desc, [self.v2.pk, self.v1.pk])

    def test_catalogo_pagina_20_resultados(self):
        for idx in range(25):
            Vehiculo.objects.create(
                marca="Marca",
                modelo=f"Modelo {idx}",
                ano=2018,
                color="Negro",
                precio=f"{60000000 + idx}.00",
                placa=f"PAG{idx:03d}",
                categoria=self.cat_auto,
                estado=Vehiculo.Estado.USADO,
                activo=True,
                vendedor=self.vendedor,
            )

        response = self.client.get(reverse("catalogo"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["vehiculos"]), 20)
        self.assertEqual(response.context["page_obj"].paginator.count, 27)
        self.assertEqual(response.context["page_obj"].paginator.num_pages, 2)

        response_page2 = self.client.get(reverse("catalogo"), {"page": 2})
        self.assertEqual(len(response_page2.context["vehiculos"]), 7)


class CambioRolTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="dual_user",
            password="123456",
            is_staff=True,
        )
        compradores, _ = Group.objects.get_or_create(name="Compradores")
        vendedores, _ = Group.objects.get_or_create(name="Vendedores")
        self.user.groups.add(compradores, vendedores)

    def test_cambiar_a_vendedor_desde_catalogo_redirige_admin(self):
        self.client.login(username="dual_user", password="123456")
        session = self.client.session
        session["rol_activo"] = "comprador"
        session.save()

        response = self.client.get(
            reverse("cambiar_rol"),
            {"rol": "vendedor", "next": "/catalogo/"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/")
        self.assertEqual(self.client.session.get("rol_activo"), "vendedor")

    def test_cambiar_a_comprador_desde_admin_redirige_home(self):
        self.client.login(username="dual_user", password="123456")
        session = self.client.session
        session["rol_activo"] = "vendedor"
        session.save()

        response = self.client.get(
            reverse("cambiar_rol"),
            {"rol": "comprador", "next": "/admin/"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertEqual(self.client.session.get("rol_activo"), "comprador")


class VehiculoRF4ValidationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.vendedor = user_model.objects.create_user(
            username="rf4_vendedor",
            password="123456",
            is_staff=True,
        )
        self.categoria = Categoria.objects.create(nombre="Camioneta")

    def _vehiculo(self, placa):
        return Vehiculo(
            marca="Toyota",
            modelo="Hilux",
            ano=2020,
            color="Blanco",
            precio="180000000.00",
            placa=placa,
            categoria=self.categoria,
            estado=Vehiculo.Estado.USADO,
            activo=True,
            vendedor=self.vendedor,
        )

    def test_rf4_rechaza_placa_duplicada_con_mensaje(self):
        Vehiculo.objects.create(
            marca="Ford",
            modelo="Ranger",
            ano=2019,
            color="Negro",
            precio="150000000.00",
            placa="ABC123",
            categoria=self.categoria,
            estado=Vehiculo.Estado.USADO,
            activo=True,
            vendedor=self.vendedor,
        )

        vehiculo_duplicado = self._vehiculo("ABC123")

        with self.assertRaises(ValidationError) as error:
            vehiculo_duplicado.full_clean()

        self.assertIn("placa", error.exception.message_dict)
        self.assertIn(
            "Ya existe un vehículo registrado con esa placa.",
            error.exception.message_dict["placa"],
        )

    def test_rf4_rechaza_placa_duplicada_sin_importar_mayusculas(self):
        Vehiculo.objects.create(
            marca="Ford",
            modelo="Ranger",
            ano=2019,
            color="Negro",
            precio="150000000.00",
            placa="ABC123",
            categoria=self.categoria,
            estado=Vehiculo.Estado.USADO,
            activo=True,
            vendedor=self.vendedor,
        )

        vehiculo_duplicado = self._vehiculo("abc123")

        with self.assertRaises(ValidationError) as error:
            vehiculo_duplicado.full_clean()

        self.assertIn(
            "Ya existe un vehículo registrado con esa placa.",
            error.exception.message_dict["placa"],
        )

    def test_rf4_normaliza_placa_al_guardar(self):
        vehiculo = self._vehiculo("  abc123  ")
        vehiculo.save()
        vehiculo.refresh_from_db()

        self.assertEqual(vehiculo.placa, "ABC123")
