import config

from bottle import route
from bottle import request
from bottle import response

from datetime import datetime

from services.http import httpservice
from services.engine import postservice

@route("%s/post/<year:int>/<month:int>/<slug>" % config.PUBLIC_API_PREFIX, method="GET")
def getPost(year, month, slug):
	logger = logging.getLogger(__name__)

	try:
		post = postservice.getPostByDateAndSlug(year=year, month=month, slug=slug)

		if post:
			return postservice.makePageFriendlyPost(post)
		else:
			return httpservice.notFound(response=response, message="Post not found")

	except Exception as e:
		logger.error(e.message, exc_info=True)
		return httpservice.error(response=response, message="There was a problem processing your request")
