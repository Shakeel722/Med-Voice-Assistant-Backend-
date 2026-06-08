"""
Database Configuration Module

This file manages database settings for the Med Voice Assistant backend.
It supports multiple database backends and can be easily modified to use
external databases built by other team members.

To switch databases:
1. Update the DATABASES dict below
2. Or set environment variables (DB_ENGINE, DB_HOST, DB_PORT, etc.)
3. Restart the Django server
"""

import os

# Default: PostgreSQL for this workspace (change via env vars if needed)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'medical_assistant'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres@shakeel'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ============================================================================
# FUTURE: External Database Configuration
# ============================================================================
# When your friend builds the database, update the DATABASES dict below:
#
# PostgreSQL Example:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('DB_NAME', 'medvoice_db'),
#         'USER': os.getenv('DB_USER', 'postgres'),
#         'PASSWORD': os.getenv('DB_PASSWORD', ''),
#         'HOST': os.getenv('DB_HOST', 'localhost'),
#         'PORT': os.getenv('DB_PORT', '5432'),
#     }
# }
#
# MySQL Example:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.getenv('DB_NAME', 'medvoice_db'),
#         'USER': os.getenv('DB_USER', 'root'),
#         'PASSWORD': os.getenv('DB_PASSWORD', ''),
#         'HOST': os.getenv('DB_HOST', 'localhost'),
#         'PORT': os.getenv('DB_PORT', '3306'),
#     }
# }
#
# MongoDB Example (with djongo):
# DATABASES = {
#     'default': {
#         'ENGINE': 'djongo',
#         'NAME': os.getenv('MONGO_DB_NAME', 'medvoice_db'),
#         'ENFORCE_SCHEMA_CHECK': False,
#         'CLIENT': {
#             'host': os.getenv('MONGO_HOST', 'localhost'),
#             'port': int(os.getenv('MONGO_PORT', 27017)),
#         }
#     }
# }
# ============================================================================

# Environment-based override
DB_ENGINE = os.getenv('DB_ENGINE')
if DB_ENGINE:
    if DB_ENGINE == 'postgresql':
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'medvoice_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres@shakeel'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    elif DB_ENGINE == 'mysql':
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'medvoice_db'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres@shakeel'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
        }
