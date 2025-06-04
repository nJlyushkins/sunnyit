import os, sys
sys.path.insert(0, '/var/www/u2783929/data/www/sunnyit.online/sunnybots')
sys.path.insert(1, '/var/www/u2783929/data/djangoenv/lib/python3.9/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sunnybots.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()