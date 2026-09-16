import sys

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import ProgrammingError
from django.db.backends.postgresql.base import DatabaseWrapper
from django.db.backends.signals import connection_created
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


@receiver(post_save, sender='netbox_secrets.UserKey')
@receiver(post_delete, sender='netbox_secrets.UserKey')
def invalidate_auto_master_key_cache(sender, **kwargs):
    """
    Clear the cached auto-unlock master key whenever a UserKey changes.

    Without this, activating/rotating/deleting the UserKey that backs the
    configured ``private_key`` setting would only take effect after a
    process restart.
    """
    from .utils import clear_auto_master_key_cache

    clear_auto_master_key_cache()


@receiver(connection_created, sender=DatabaseWrapper)
def configure_generic_relations(sender, **kwargs):
    if 'test' in sys.argv:
        # Skip this signal during tests to avoid issues with test database destruction
        return

    from .constants import SECRET_ASSIGNABLE_MODELS

    try:
        for content_type in ContentType.objects.filter(SECRET_ASSIGNABLE_MODELS):
            model_class = content_type.model_class()
            if model_class is None:
                continue
            if not hasattr(model_class, 'secrets'):
                GenericRelation(
                    to='netbox_secrets.Secret',
                    content_type_field='assigned_object_type',
                    object_id_field='assigned_object_id',
                    related_query_name=str(content_type.model),
                ).contribute_to_class(
                    model_class,
                    'secrets',
                )

    except ProgrammingError:
        # DB may still not be ready during very early migrations
        pass
