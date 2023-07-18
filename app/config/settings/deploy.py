from .base import *

config_secret_deploy = json.loads(open(CONFIG_SECRET_DEPLOY_FILE).read())

# secret setting
DEBUG = False
ALLOWED_HOSTS = config_secret_deploy['django']['allowed_hosts']
CSRF_TRUSTED_ORIGINS = config_secret_deploy['django']['csrf_trusted_origins']

# aws
AWS_ACCESS_KEY_ID = config_secret_deploy['django']['aws_access_key_id']
AWS_SECRET_ACCESS_KEY = config_secret_deploy['django']['aws_secret_access_key']

# WSGI application
WSGI_APPLICATION = 'config.wsgi.deploy.application'
