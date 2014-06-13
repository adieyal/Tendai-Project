import os
import site
import sys

project_name = "tendai"

virtualenv_home = os.path.join(os.environ["HOME"], ".virtualenvs", project_name)

site.addsitedir(os.path.join(virtualenv_home, "lib", "python2.7", "site-packages"))
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % project_name

activate_this = os.path.join(virtualenv_home, "bin", "activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

server_root = os.path.join(os.environ["HOME"], "webapps", project_name)
site_root = os.path.join(server_root, project_name)
sys.path.append(server_root)
sys.path.append(site_root)

from django.core.handlers.wsgi import WSGIHandler
from paste.exceptions.errormiddleware import ErrorMiddleware

application = WSGIHandler()
application = ErrorMiddleware(application, debug=True)

