import logging
import os

from lizard_ui.settingshelper import STATICFILES_FINDERS

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s %(levelname)s %(message)s')

DEBUG = True
TEMPLATE_DEBUG = True
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'test.db'
SITE_ID = 1
INSTALLED_APPS = [
    'lizard_wms',
    'lizard_ui',
    'lizard_map',
    'lizard_maptree',
    'lizard_security',
    'south',
    'staticfiles',
    'compressor',
    'django_nose',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    ]
ROOT_URLCONF = 'lizard_wms.urls'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test.db'},
    }

TEMPLATE_CONTEXT_PROCESSORS = (
    # Default items.
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    # Needs to be added for django-staticfiles to allow you to use
    # {{ STATIC_URL }}myapp/my.css in your templates.
    'staticfiles.context_processors.static_url',
    # For lizard-map
    "django.core.context_processors.request",
    )


# SETTINGS_DIR allows media paths and so to be relative to this settings file
# instead of hardcoded to c:\only\on\my\computer.
SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))

# BUILDOUT_DIR is for access to the "surrounding" buildout, for instance for
# BUILDOUT_DIR/var/static files to give django-staticfiles a proper place
# to place all collected static files.
BUILDOUT_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '..'))


# Absolute path to the directory that holds user-uploaded media.
MEDIA_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'media')
# Absolute path to the directory where django-staticfiles'
# "bin/django build_static" places all collected static files from all
# applications' /media directory.
STATIC_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'static')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
MEDIA_URL = '/media/'
# URL for the per-application /media static files collected by
# django-staticfiles.  Use it in templates like
# "{{ MEDIA_URL }}mypackage/my.css".
STATIC_URL = '/static_media/'
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.  Uses STATIC_URL as django-staticfiles nicely collects
# admin's static media into STATIC_ROOT/admin.
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Almere base layer
MAP_SETTINGS = {
    'base_layer_type': 'WMS',  # OSM or WMS
    'projection': 'EPSG:28992',  # EPSG:900913, EPSG:28992
    'display_projection': 'EPSG:28992',  # EPSG:900913/28992/4326
    'startlocation_x': '127000',
    'startlocation_y': '473000',
    'startlocation_zoom': '4',
    'base_layer_wms': (
        'http://kaart.almere.nl/wmsconnector/com.esri.wms.Esrimap?'
        'SERVICENAME=AIKWMS&'),
    'base_layer_wms_layers': (
        'KLHOpenbaargebied,KLHBebouwing,KLHBedrijventerrein,KLHBos,'
        'KLHWater,KLHStrand,KLHHoofdweg,KLHWeg,KLHVliegveld,KLHSnelweg,'
        'KLHGemeentegrens,KLHBusbaan,KLHSpoorlijn,KLHTeksten,'
        'KLTAutosnelweg,KLTBebouwingCentrum,KLTBedrijven,'
        'KLTBedrijventerrein,KLTBijzondereBebouwing,KLTBosvak,KLTCentrum,'
        'KLTFietspad,KLTGras,KLTHoofdweg,KLTLandbouwVeeteelt,KLTMoerasNatuur,'
        'KLTOVbaan,KLTOverigePaden,KLTSpoorlijnWit,KLTSpoorlijnZwart,'
        'KLTSportvelden,KLTSteiger,KLTStrand,KLTWater,KLTWijkwegen,'
        'KLTWoningen,KLTWoongebied,KLTGemeentegrens,KLTHoogspanningsleiding,'
        'KLTHoogspanningsmasten,KLTInOntwerp,KLTKabelbaan,KLTKavelsloot,'
        'KLTWijknamen,KLTParknamen,KLTOpenwaternamen,KLTIndustrienamen,'
        'KLTDreefnamen,GBKAWater,GBKAGras,GBKAPlantvak,GBKABeton,GBKABosvak,'
        'GBKABraakLiggend,GBKAAsfalt'),
    }


# MAP_SETTINGS = {
#     'base_layer_type': 'WMS',  # OSM or WMS
#     'projection': 'EPSG:28992',  # EPSG:900913, EPSG:28992
#     'display_projection': 'EPSG:28992',  # EPSG:900913/28992/4326
#     'startlocation_x': '127000',
#     'startlocation_y': '473000',
#     'startlocation_zoom': '4',
#     'base_layer_wms': (
#         'http://nederlandwms.risicokaart.nl/wmsconnector/'
#         'com.esri.wms.Esrimap?'
#         'SERVICENAME=risicokaart_pub_nl_met_ondergrond&'),
#     'base_layer_wms_layers': (
#         'Outline_nederland,Dissolve_provincies,0,2,12,3,38,5,4,9,10'),
#     }

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

LIZARD_WMS_STANDALONE = True

try:
    # Import local settings that aren't stored in svn.
    from lizard_wms.local_testsettings import *
except ImportError:
    pass
