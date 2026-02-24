from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LogoutView
from django.views.generic.base import RedirectView

urlpatterns = [
    path("admin/logout/", LogoutView.as_view(next_page='/'), name='admin-logout'),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    # redirect any stray accounts/login requests to our custom login
    path("accounts/login/", RedirectView.as_view(pattern_name='site_login', permanent=False)),
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
