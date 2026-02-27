from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("health/", views.health, name="health"),
    # custom login route at /login (alias for accounts/login/)
    path("login/", views.CustomLoginView.as_view(), name="site_login"),
    path("cambiar-rol/", views.cambiar_rol, name="cambiar_rol"),
]
