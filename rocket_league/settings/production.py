from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'opbeat.contrib.django',
)

OPBEAT = {
    'ORGANIZATION_ID': '2dd102f6d15e4d888e5683e14a799465',
    'APP_ID': 'cfa7fb31c9',
    'SECRET_TOKEN': '91d4ab84522796df52c4571568cfd6f1583b9e1d',
}

MIDDLEWARE_CLASSES = (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
) + MIDDLEWARE_CLASSES

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'opbeat': {
            'level': 'WARNING',
            'class': 'opbeat.contrib.django.handlers.OpbeatHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'rocket_league': {
            'level': 'WARNING',
            'handlers': ['opbeat'],
            'propagate': False,
        },
        # Log errors from the Opbeat module to the console (recommended)
        'opbeat.errors': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# S3 settings.
DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"
STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"

# The region to connect to when storing files.
AWS_REGION = "eu-west-1"

# The AWS access key used to access the storage buckets.
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')

# The AWS secret access key used to access the storage buckets.
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')

# The S3 bucket used to store uploaded files.
AWS_S3_BUCKET_NAME = "media.rocketleaguereplays.com"

# The S3 calling format to use to connect to the bucket.
AWS_S3_CALLING_FORMAT = "boto.s3.connection.OrdinaryCallingFormat"

# Whether to enable querystring authentication for uploaded files.
AWS_S3_BUCKET_AUTH = False

# The expire time used to access uploaded files.
AWS_S3_MAX_AGE_SECONDS = 60 * 60 * 24 * 365  # 1 year.

# The S3 bucket used to store static files.
AWS_S3_BUCKET_NAME_STATIC = "static.rocketleaguereplays.com"

# The S3 calling format to use to connect to the static bucket.
AWS_S3_CALLING_FORMAT_STATIC = "boto.s3.connection.OrdinaryCallingFormat"

# Whether to enable querystring authentication for static files.
AWS_S3_BUCKET_AUTH_STATIC = False

# The expire time used to access static files.
AWS_S3_MAX_AGE_SECONDS_STATIC = 60 * 60 * 24 * 365  # 1 year.

COMPRESS_URL = "https://{}/".format(
    AWS_S3_BUCKET_NAME_STATIC,
)

MEDIA_URL = "https://{}/".format(
    AWS_S3_BUCKET_NAME,
)

STATIC_URL = COMPRESS_URL
COMPRESS_STORAGE = 'django_s3_storage.storage.StaticS3Storage'

MEDIA_ROOT = '/'
COMPRESS_ROOT = STATIC_ROOT

AWS_S3_PUBLIC_URL = MEDIA_URL
AWS_S3_PUBLIC_URL_STATIC = STATIC_URL
