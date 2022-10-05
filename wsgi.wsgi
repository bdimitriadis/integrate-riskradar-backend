#!/usr/bin/python3
import sys
import logging


# sys.path.append("/var/www/FlaskApp/FlaskApp")


logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/html/FlaskApp")
from FlaskApp import app as application

# application.secret_key = 'Thisissupposedtobesecret!'

# if path not in sys.path:
#     sys.path.insert(0, path)
