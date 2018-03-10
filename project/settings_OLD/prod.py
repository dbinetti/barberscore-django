# Local
from .base import *

# Core
DEBUG = False
ALLOWED_HOSTS = [
    '.barberscore.com',
    '.herokuapp.com',
]

# Databases
DATABASES['bhs_db'] = dj_database_url.parse(
    get_env_variable("BHS_DATABASE_URL"),
    conn_max_age=600,
)
DATABASE_ROUTERS = [
    'routers.BHSRouter',
]

# Caches
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": get_env_variable("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 40},
        }
    },
}

# Auth0
AUTH0_CLIENT_ID = get_env_variable("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = get_env_variable("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = get_env_variable("AUTH0_DOMAIN")
AUTH0_API_ID = get_env_variable("AUTH0_API_ID")
AUTH0_API_SECRET = get_env_variable("AUTH0_API_SECRET")
AUTH0_AUDIENCE = get_env_variable("AUTH0_AUDIENCE")

# JWT Settings
from cryptography import x509
from cryptography.hazmat.backends import default_backend

pem_data = b"""
-----BEGIN CERTIFICATE-----
MIIDBTCCAe2gAwIBAgIJed2q4tV5RkohMA0GCSqGSIb3DQEBCwUAMCAxHjAcBgNV
BAMTFWJhcmJlcnNjb3JlLmF1dGgwLmNvbTAeFw0xODAyMDkxODAyMDdaFw0zMTEw
MTkxODAyMDdaMCAxHjAcBgNVBAMTFWJhcmJlcnNjb3JlLmF1dGgwLmNvbTCCASIw
DQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMFIohIOwEybtBK5S4e4mmZGmY7A
IscyRWZ4CxrEfq8hbcQCLOav96nfVUOtRskq6oS/rZbzsexil4v3ocAO0U3sc9KR
82Cahyk1d0Duma0m4q8ZTXG9roen3EE7LJoJhWXJ/JSY7CKQRe40OPhK2Tv1Y4Ni
E1doTFtrgeSCwjUnd0oFNjL+9VLOivQETSBsva2gAJir04s+at2CIm+WyNaj76zb
D/Fiqqpm2z+OVyfzKun13M2wFXjCAt3VZSYMt7NrGkXxf0n16HcZuXuP2qn6riki
7aauB8EP7O3BKYGeZQSN9/ydax5WH08vtsVTNLcYWD1a4Ws2ksXZ5eWv5eUCAwEA
AaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUgJ/ErsXOk1PdmFh5e7QQ
Z2UJ6LUwDgYDVR0PAQH/BAQDAgKEMA0GCSqGSIb3DQEBCwUAA4IBAQC3lNOitMi2
9L3pfS90bq1/0DZ40rQvGZPsfW8BtzqjLfeXZOdh7KKcwvQ9vtXVc0x7vDIrceTl
h1BMNpf2kJvDEwukx/oyf+Pf7SSUdCZTfd8ZYqWoHoooh2GjmDhV8kPm4MHukqA+
saVEQOA50nCahvVUsSeBssTT5o5NwxKi15o3Q2WeRrB0otYBwIM6DG53ag7KCi9N
KiONK1IrUyr29xUwiVZyLBOMUvdNwcvySpgF8+7/2vj7tDXvtCtKkXoHeXNPe6wH
pY05d2kke4kiZUNcyQ9TBRMjir8A5qEQwJtCJuPNPPrhg3RoHag4IhculfCZjYot
v/6+C6H1b1go
-----END CERTIFICATE-----
""".strip()
cert = x509.load_pem_x509_certificate(pem_data, default_backend())
jwt_public_key = cert.public_key()


def jwt_get_username_from_payload_handler(payload):
    return payload.get('email')

JWT_AUTH = {
    'JWT_AUDIENCE': AUTH0_CLIENT_ID,
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': jwt_get_username_from_payload_handler,
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_PUBLIC_KEY': jwt_public_key,
    'JWT_ALGORITHM': 'RS256',
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_PORT = 587
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = get_env_variable("SENDGRID_API_KEY")
EMAIL_USE_TLS = True

# Cloudinary
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
CLOUDINARY_URL = get_env_variable("CLOUDINARY_URL")
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Algolia
ALGOLIA = {
    'APPLICATION_ID': get_env_variable("ALGOLIASEARCH_APPLICATION_ID"),
    'API_KEY': get_env_variable("ALGOLIASEARCH_API_KEY"),
    'AUTO_INDEXING': True,
}

# Heroku
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

# Sentry
RAVEN_CONFIG = {
    'environment': 'production',
    'dsn': get_env_variable("SENTRY_DSN"),
    'release': get_env_variable("HEROKU_RELEASE_VERSION"),
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'api': {
            'handlers': [
                'console',
            ],
            'level': 'INFO',
        },
        'importer': {
            'handlers': [
                'console',
            ],
            'level': 'INFO',
        },
        'updater': {
            'handlers': [
                'console',
            ],
            'level': 'INFO',
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': [
                'console'
            ],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': [
                'console'
            ],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': [
                'console'
            ],
            'propagate': False,
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
    },
}

INSTALLED_APPS += [
    'raven.contrib.django.raven_compat',
    'algoliasearch_django',
]