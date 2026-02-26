from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from core.roles import GROUP_VENDEDORES


User = get_user_model()


@receiver(m2m_changed, sender=User.groups.through)
def sync_is_staff_with_groups(sender, instance, action, **kwargs):
    if action not in {"post_add", "post_remove", "post_clear"}:
        return

    if instance.is_superuser:
        return

    es_vendedor = instance.groups.filter(name=GROUP_VENDEDORES).exists()
    nuevo_is_staff = es_vendedor

    if instance.is_staff != nuevo_is_staff:
        instance.is_staff = nuevo_is_staff
        instance.save(update_fields=["is_staff"])

