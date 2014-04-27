#
# File: bottle_starter.py
# Bottle plugin that runs every request. This wrapper performs
# the following tasks.
#
#    - Establishes a database connection
#    - Determine the theme name and configures pathing
#    - Concatenates URL and FORM variables into *request.all*
#    - Configures timezone requirements
#    - Executes requested action and view
#    - Disconnects from the database
#
# Author:
#    Adam Presley
#
import re
import bottle
import config
import database

from bottle import request
from bottle import redirect
from bottle import response

from services.installer import installservice
from services.engine import engineservice

def starter(callback):
	def wrapper(*args, **kwargs):
		#
		# Connect to our database
		#
		if len(config.ENVIRONMENT["DB_HOST"]):
			database.connect(
				engine   = "mysql",
				host     = config.ENVIRONMENT["DB_HOST"],
				port     = config.ENVIRONMENT["DB_PORT"],
				database = config.ENVIRONMENT["DB_NAME"],
				user     = config.ENVIRONMENT["DB_USER"],
				password = config.ENVIRONMENT["DB_PASSWORD"]
			)

		request.all = dict(list(request.query.items()) + list(request.forms.items()))

		if installservice.isEngineInstalled():
			request.timezone = engineservice.getBlogTimezone()
			config.TIMEZONE = request.timezone
		else:
			config.TIMEZONE = "UTC"

		#
		# Finally call the the next method in the chain
		#
		body = callback(*args, **kwargs)
		database.disconnect()

		return body

	return wrapper

