import config

from bottle import route
from bottle import request
from bottle import response

from datetime import datetime

from services.http import httpservice
from services.engine import postservice

@route("%s/tags" % config.PUBLIC_API_PREFIX, method="GET")
def getTagCollection():
	logger = logging.getLogger(__name__)

	try:
		return {
			"tags": postservice.getPostTags()
		}

	except Exception as e:
		logger.error(e.message, exc_info=True)
		return httpservice.error(response=response, message="There was a problem processing your request")
