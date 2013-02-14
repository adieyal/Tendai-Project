#!/usr/bin/python
import os, site, sys

# Tell wsgi to add the Python site-packages to its path.
site.addsitedir('/var/www/tendai.medicinesinfohub.net/env/lib/python2.7/site-packages')

# Fix markdown.py (and potentially others) using stdout
sys.stdout = sys.stderr

# Calculate the path based on the location of the WSGI script.
project = os.path.dirname(__file__)
workspace = os.path.dirname(project)
sys.path.append(workspace)

os.environ["DJANGO_SETTINGS_MODULE"] = 'tendai.settings_siteone'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

from django.conf import settings
sys.path.insert(0, settings.PROJECT_ROOT)
