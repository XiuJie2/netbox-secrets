# Setup (Installation & Configuration)

## Requirements

- A supported NetBox installation
- Python environment with access to NetBox dependencies
- Database already configured for NetBox

## Install from PyPI

```shell
pip install netbox-secrets
```

## Install from Source (development)

```shell
git clone <your-fork-or-repo-url>
cd netbox-secrets
pip install -e .
```

## Enable the Plugin

Add the plugin to NetBox configuration:

```python
# configuration.py
PLUGINS = [
    'netbox_secrets',
]
```

## Configure the Plugin

NetBox Secrets is configured via `PLUGINS_CONFIG` in `configuration.py`.

### Required Settings

#### `apps`

A list of NetBox models where secrets can be assigned and displayed. Each entry is `app_label.model`.

Example:

```python
PLUGINS_CONFIG = {
    'netbox_secrets': {
        'apps': [
            'dcim.device',
            'virtualization.virtualmachine',
        ],
    }
}
```

### Optional Settings

#### `display_default`

Controls where the secrets panel appears on supported object pages.

- Type: `str`
- Default: `tab_view`
- Allowed values: `left_page`, `right_page`, `full_width_page`, `tab_view`

#### `display_setting`

Overrides `display_default` per model.

- Type: `dict`
- Example:

```python
PLUGINS_CONFIG = {
    'netbox_secrets': {
        'apps': ['dcim.device', 'virtualization.virtualmachine'],
        'display_default': 'tab_view',
        'display_setting': {
            'dcim.device': 'full_width_page',
            'virtualization.virtualmachine': 'right_page',
        },
    }
}
```

#### `public_key_size`

Minimum RSA key size allowed for user keys. This is also the default size used when generating a new key pair from the UI or API without an explicit `key_size`.

- Type: `int`
- Default: `2048`

#### `top_level_menu`

Whether the plugin appears as a top-level menu item.

- Type: `bool`
- Default: `False`

#### `private_key`

RSA private key (PEM) used to automatically resolve the master key on every request. This removes the need for
users to submit their private key or refresh an expiring session key — once configured, any authenticated user
with `view_secret`/`change_secret` permission can read and write secrets without any further verification step.

- Type: `str` (PEM-encoded RSA private key)
- Default: not set

The key must correspond to an **already-activated** User Key (its `master_key_cipher` must be decryptable with
this private key) — see [Cryptography](cryptography.md). If this setting is absent, creating or updating a
secret fails with "No master key is available", and reading a secret returns it still encrypted.

Example:

```python
PLUGINS_CONFIG = {
    'netbox_secrets': {
        'apps': ['dcim.device', 'virtualization.virtualmachine'],
        'private_key': open('/etc/netbox/secrets_private_key.pem').read(),
    }
}
```

> **Security note:** configuring `private_key` removes the private-key verification that normally gates secret
> decryption. Anyone with `view_secret` permission — and anyone who can read the NetBox configuration file or
> process memory — can decrypt secrets without any additional authentication. Store the private key file with
> restrictive filesystem permissions (e.g. `chmod 600`), keep it out of version control, and treat it as a
> NetBox-wide secret in its own right.

### Related NetBox Settings

If `private_key` is **not** configured, secrets fall back to the manual per-user flow described in the
[Usage Guide](usage.md#3-create-a-session-key), where these standard NetBox settings affect the session key
cookie's lifetime and transport security:

- `SESSION_COOKIE_SECURE`
- `LOGIN_TIMEOUT`

Once `private_key` is configured, these settings no longer affect secret decryption — see [`private_key`](#private_key)
above.

## Run Migrations and Collect Static Files

```shell
./manage.py migrate
./manage.py collectstatic --no-input
```

## Upgrade

1) Upgrade the package

```shell
pip install --upgrade netbox-secrets
```

2) Run migrations and collectstatic again

```shell
./manage.py migrate
./manage.py collectstatic --no-input
```

## Uninstall

1) Remove the plugin from `PLUGINS` in `configuration.py`
2) Uninstall the package: `pip uninstall netbox-secrets`
