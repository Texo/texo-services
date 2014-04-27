#
# File: texo.py
# This is the main application entry script. This is what is executed
# to run a Texo CMS application. The boostrap process performs the
# following actions.
#
# Bootstrap process:
#    * Establish a DB connection
#    * Import controllers
#    * Setup framework template paths
#    * Initialize the pre-request processor hook
#    * Prepare the session middleware
#    * Run the application
#
# Author:
#    Adam Presley
#
import os
import sys

#
# Add current and parent path to syspath
#
currentPath = os.path.dirname(__file__)
parentPath = os.path.abspath(os.path.join(currentPath, os.path.pardir))

sys.path.append(currentPath)
sys.path.append(parentPath)

#
# Import framework and config
#
import config
import bottle
import bottle_starter

from bottle import install
from bottle import TEMPLATE_PATH

from services.engine import engineservice

if engineservice.getDebugSetting():
	sys.dont_write_bytecode = True

engineservice.configureLogging()
engineservice.importControllers()

if engineservice.getDebugSetting():
	print("Installing pre-request hook...")

install(bottle_starter.starter)

bottle.debug(engineservice.getDebugSetting())
engineservice.runApp(app=bottle.app())
