#! var/www/universityJobDay/universityJobDay/.venv/bin/python

import sys

sys.path.insert(0,"/var/www/universityJobDay/universityJobDay/")

activate_this = '/var/www/universityJobDay/universityJobDay/.venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))


from app_uni import app as application
