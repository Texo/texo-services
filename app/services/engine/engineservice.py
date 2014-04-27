#
# File: engineservice.py
# This module offers functions to support core Texo CMS
# engine services. It is used to get configuration information,
# setup logging, and start application services. The main
# application entry-point uses functions here to import controllers,
# set theme paths, and start the application engine.
#
# Author:
#    Adam Presley
#
import os
import bottle
import config
import logging
import database
import logging.handlers

from bottle import run

#
# Function: configureLogging
# Sets up a rotating file log called *application.log* in
# ROOT_PATH. It is configured to reach 20MB before going
# to backup. Currently only two backup logs are kept before
# deletion.
#
# Logs are kept in the following format
#    > Time - Name - Level - Message
#
def configureLogging():
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)

	fileHandler = logging.handlers.RotatingFileHandler(filename=os.path.join(config.ROOT_PATH, "application.log"), maxBytes=20480000, backupCount=2)
	fileHandler.setLevel(logging.DEBUG)

	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	fileHandler.setFormatter(formatter)

	logger.addHandler(fileHandler)

#
# Function: getBlogTimezone
# Returns the blog's timezone. The timezone is set in the user interface
# under *Settings* and is stored in the database in the table *settings*.
#
def getBlogTimezone():
	settings = getSettings()
	return settings["timezone"]

#
# Function: getDebugSetting
# Queries the OS environment for the key *TEXO_SETTINGS_DEBUG*
# to set the application debug flag. If the environment
# key is not found the default value is False.
#
def getDebugSetting():
	return os.getenv("TEXO_SETTINGS_DEBUG", False)

#
# Function: getInstalledThemeNames
# Gets directory names from the theme path at THEME_PATH and
# returns them as a list.
#
def getInstalledThemeNames():
	return os.listdir(config.THEME_PATH)

#
# Function: getSettings
# Queries the database for blog settings. If there are no blog
# settings in the database an exception is thrown.
#
# Throws:
#    Throws an exception when no settings are found
#
def getSettings():
	qrySettings = database.query(sql="""
		SELECT
			themeName,
			timezone
		FROM settings
	""")

	if len(qrySettings) <= 0:
		raise Exception("There was a problem loading your settings")

	return qrySettings[0]

#
# Function: importControllers
# Imports all relevant Python controller files found in the directory
# at CONTROLLER_PATH. Used during the bootstrap process in *texo.py*.
#
def importControllers():
	logger = logging.getLogger(__name__)

	for controllerItem in filter(lambda x: x.endswith(".py") and x != "__init__.py", os.listdir(config.CONTROLLER_PATH)):
		fileName, ext = os.path.splitext(controllerItem)
		logger.debug("Importing controller %s" % fileName)

		exec("from www.controllers import %s" % fileName)

#
# Function: runApp
# Executes a Bottle application as setup in the variable *app*.
# This is run during the bootstrap process from *texo.py*.
#
# Parameters:
#    app - Bottle application reference
#
def runApp(app):
	logger = logging.getLogger(__name__)

	logger.debug("Starting server on %s:%s (DEBUG == %s)" % (config.ENVIRONMENT["BIND_TO_HOST"], config.ENVIRONMENT["BIND_TO_PORT"], getDebugSetting()))

	if getDebugSetting():
		run(app=app, host="0.0.0.0", port=config.ENVIRONMENT["BIND_TO_PORT"], reloader=True, debug=True)
	else:
		run(app=app, host=config.ENVIRONMENT["BIND_TO_HOST"], port=config.ENVIRONMENT["BIND_TO_PORT"], server="gunicorn", workers=config.ENVIRONMENT["NUM_WORKER_PROCESSES"], proc_name=config.ENVIRONMENT["PROCESS_NAME"], daemon=False)

#
# Function: saveSettings
# Saves blog settings to the database.
#
# Parameters:
#    timezone - Valid timezone name string
#    theme    - Theme directory name (not path)
#
def saveSettings(timezone, theme):
	database.query(sql="""
		UPDATE settings SET
			  timezone=%s
			, themeName=%s
	""", parameters=(
		timezone,
		theme,
	))

#
# Function: setupTemplatePaths
# Sets template paths in the Bottle framework.
#
def setupTemplatePaths():
	logger = logging.getLogger(__name__)

	bottle.TEMPLATE_PATH.append(config.BASE_TEMPLATE_PATH)
	logger.debug("Template path: %s" % bottle.TEMPLATE_PATH)
