import config

from bottle import route
from bottle import request
from bottle import response

from datetime import datetime

from services.http import httpservice
from services.engine import postservice

@route("%s/tag/<id:int>" % config.PUBLIC_API_PREFIX, method="GET")
def getTag(id):
	logger = logging.getLogger(__name__)

	try:
		tag = postservice.getPostTagById(id=id)

		if tag:
			return postservice.makeFriendlyTag(tag=tag)
		else:
			return httpservice.notFound(response=response, message="Tag not found")

	except Exception as e:
		logger.error(e.message, exc_info=True)
		return httpservice.error(response=response, message="There was a problem processing your request")
