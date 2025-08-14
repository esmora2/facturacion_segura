
"""Configuración principal de Django para facturacion_segura."""

from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', cast=bool)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.9.7.150', '10.40.0.99', '*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'apps.usuarios',
    'apps.clientes',
    'apps.productos',
    'apps.facturacion',
    'apps.auditorias',
    'pagos',
    'silk',
    'drf_yasg',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middlewares personalizados para control de usuarios y roles
    'apps.usuarios.middleware.CheckUserIsActiveMiddleware',
    'apps.usuarios.middleware.RoleBasedAccessMiddleware',
    'silk.middleware.SilkyMiddleware',
    # Middleware para profiling automático de APIs
    'apps.auditorias.middleware.AutoSilkProfilingMiddleware',
]

ROOT_URLCONF = 'facturacion_segura.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'facturacion_segura.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10,
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
]
CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'usuarios.User'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Configuración de Django Silk para profiling
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_PYTHON_PROFILER_RESULT_PATH = BASE_DIR / 'profiles'
SILKY_ANALYZE_QUERIES = True
SILKY_RECORD_REQUESTS = True
SILKY_INTERCEPT_PERCENT = 100  # Captura el 100% de las requests
SILKY_MAX_REQUEST_BODY_SIZE = -1  # Sin límite en el tamaño del body
SILKY_MAX_RESPONSE_BODY_SIZE = -1  # Sin límite en el tamaño de la respuesta
SILKY_AUTHENTICATION = True  # Requiere autenticación para acceder a Silk
SILKY_AUTHORISATION = True  # Requiere autorización
SILKY_PYTHON_PROFILER = True  # Profiler de Python activo
SILKY_PYTHON_PROFILER_BINARY = True  # Profiler binario activo
SILKY_PYTHON_PROFILER_RESULT_PATH = '/tmp/'  # Ruta temporal para profiler
SILKY_MAX_REQUEST_BODY_SIZE = -1  # Sin límite en request body
SILKY_MAX_RECORDED_REQUESTS = 100  # Limitar requests grabadas para evitar sobrecarga
SILKY_INTERCEPT_PERCENT = 100  # Interceptar 100% de requests

def silky_permissions_check(user):
    """Función para verificar permisos de Silk - solo superusuarios"""
    return user.is_superuser

SILKY_PERMISSIONS = silky_permissions_check  # Solo superusuarios pueden acceder

SILK_AUTHENTICATION = True  # Requiere login
SILK_AUTHORISATION = True   # Solo staff/superuser puede acceder
