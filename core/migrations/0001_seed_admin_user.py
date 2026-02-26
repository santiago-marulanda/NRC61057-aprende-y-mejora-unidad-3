import os

from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_seed_admin(apps, schema_editor):
    User = apps.get_model("auth", "User")

    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@dms.local")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "123456")

    if User.objects.filter(username=username).exists():
        return

    User.objects.create(
        username=username,
        email=email,
        password=make_password(password),
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_seed_admin, reverse_code=migrations.RunPython.noop),
    ]
