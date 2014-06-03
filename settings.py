# Django settings for riversim project.
import os
import logging

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
BASE_DIR = os.path.dirname(__file__)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'riversim',                      # Or path to database file if using sqlite3.
        'USER': 'jewart',                      # Not used with sqlite3.
        'PASSWORD': 'catfish',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = "" #os.path.join(BASE_DIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'k(5pk(ea@$@50ra^(=bmr0d$u=1+e8e8txiu3d!72-^82io!e+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'flumen.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.gis',
    'django_extensions',
    'riversim',
    'debug_toolbar',
    'south',
    'gunicorn',
    'tastypie'

    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }, 
        'null': {
            'level': 'DEBUG',
            'class':'django.utils.log.NullHandler',
         },
    },
    'loggers': {
        'django.request': {
            'handlers': ['null'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level':'DEBUG',
        },
    }
}

GEARMAN_SERVERS = ['127.0.0.1']

# debug toolbar
INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

DATA_ROOT="/Volumes/Storage/riversim"
LIDAR_TILES_PATH=os.path.join(DATA_ROOT, "lidar", "LAS")
RIVER_TILES_PATH=os.path.join(DATA_ROOT, "imagery", "TIF")
THUMBNAIL_PATH=os.path.join(DATA_ROOT, "thumbnails")
TILE_CACHE_PATH=os.path.join(DATA_ROOT, "tile_cache")
GEOTIFF_PATH=os.path.join(DATA_ROOT, "geotiff")
CHANNEL_PATH=os.path.join(DATA_ROOT, "channels")
CHANNEL_WIDTH_PATH=os.path.join(DATA_ROOT, "channel_widths")
ELEVATION_MAP_PATH=os.path.join(DATA_ROOT, "elevation_maps")
TILECACHE_CACHE=os.path.join(DATA_ROOT, "wms_tiles")

MAX_AERIAL_IMAGE_WIDTH=20000


# Tilecache
from TileCache import Service
from TileCache.Caches.Disk import Disk
from TileCache.Layers import GDAL 

diskCache = Disk(TILECACHE_CACHE)
mapLayers = {}

dirList=os.listdir(GEOTIFF_PATH)
for fname in dirList:
    #'26_aerial': GDAL.GDAL("26_aerial", "/data/riversim/geotiff/26.tiff"),
    #'26_channels': GDAL.GDAL("26_channels", "/data/riversim/channels/26.tiff"),
    #'26_width': GDAL.GDAL("26_width", "/data/riversim/channel_widths/26.tiff")
    #print fname
    if fname in (".", ".."):
        next
    print "File: %s" % (fname)
    (layer, ext) = fname.split(".")
    print "Layer: %s" % (layer)
    aerial_key = "%s_aerial" % (layer)
    channel_key = "%s_channels" % (layer)
    width_key = "%s_width" % (layer)
    try:
        mapLayers[aerial_key] = GDAL.GDAL(aerial_key, os.path.join(GEOTIFF_PATH, "%s.tiff" % (layer)))
        mapLayers[channel_key] = GDAL.GDAL(channel_key, os.path.join(CHANNEL_PATH, "%s.tiff" % (layer)))
        mapLayers[width_key] = GDAL.GDAL(width_key, os.path.join(CHANNEL_WIDTH_PATH, "%s.tiff" % (layer)))
    except:
        print "Problem adding layer %s" % (layer)




MAP_SERVICE = Service(diskCache, mapLayers)


