"""
Automatic master key resolution.

Historically, decrypting a Secret required the requesting user to submit their
RSA private key so a short-lived SessionKey could be minted; once that
SessionKey's cookie expired the user had to re-submit their private key. To
remove that repeated verification step, the master key can instead be
unlocked once from a private key held in the plugin configuration
(``PLUGINS_CONFIG["netbox_secrets"]["private_key"]``), so every authenticated
request with the appropriate NetBox permissions can decrypt secrets without
any per-session prompt.
"""

from typing import Optional

from django.conf import settings

__all__ = ['get_auto_master_key', 'clear_auto_master_key_cache']

_cached_master_key: Optional[bytes] = None
_cache_populated = False


def get_auto_master_key() -> Optional[bytes]:
    """
    Resolve the master encryption key without requiring interactive
    private-key verification.

    Reads the RSA private key from the ``private_key`` plugin setting and
    uses it to unlock the first active :class:`~netbox_secrets.models.UserKey`.
    The result is cached in-process since the underlying UserKey rarely
    changes and RSA decryption is comparatively expensive.

    Returns:
        The decrypted master key, or None if no private key is configured or
        no active UserKey exists.
    """
    global _cached_master_key, _cache_populated

    if _cache_populated:
        return _cached_master_key

    from ..models import UserKey  # Local import to avoid circular dependency

    plugin_settings = settings.PLUGINS_CONFIG.get('netbox_secrets', {})
    private_key = plugin_settings.get('private_key')

    master_key = None
    if private_key:
        user_key = UserKey.objects.active().first()
        if user_key:
            master_key = user_key.get_master_key(private_key)

    _cached_master_key = master_key
    _cache_populated = True
    return master_key


def clear_auto_master_key_cache() -> None:
    """Clear the cached master key (e.g. after UserKey rotation)."""
    global _cached_master_key, _cache_populated
    _cached_master_key = None
    _cache_populated = False
