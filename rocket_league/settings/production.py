from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'opbeat.contrib.django',
)

OPBEAT = {
    "ORGANIZATION_ID": "dde034beb33d4b77bb9937c39f0c158f",
    "APP_ID": "",
    "SECRET_TOKEN": ""
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
