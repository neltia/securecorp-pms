from .base import *

config_secret_debug = json.loads(open(CONFIG_SECRET_DEBUG_FILE).read())

# secret setting
DEBUG = True
ALLOWED_HOSTS = config_secret_debug['django']['allowed_hosts']
CSRF_TRUSTED_ORIGINS = config_secret_debug['django']['csrf_trusted_origins']

# aws
AWS_ACCESS_KEY_ID = config_secret_debug['django']['aws_access_key_id']
AWS_SECRET_ACCESS_KEY = config_secret_debug['django']['aws_secret_access_key']

# WSGI application
WSGI_APPLICATION = 'config.wsgi.debug.application'
