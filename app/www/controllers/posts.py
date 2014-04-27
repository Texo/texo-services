import config
import logging

from bottle import route
from bottle import request
from bottle import response

from datetime import datetime

from services.http import httpservice
from services.engine import postservice

@route("%s/posts/<page:int>" % config.PUBLIC_API_PREFIX, method="GET")
def getPostCollectionByPage(page):
	logger = logging.getLogger(__name__)

	try:
		posts, postCount, numPages = postservice.getPosts(page=page, status="Published", postsPerPage=config.POSTS_PER_PAGE)

		if int(postCount) > 0:
			return {
				"posts": map(postservice.makePageFriendlyPost, posts),
				"numPages": int(numPages),
				"numPosts": int(postCount)
			}
		else:
			return httpservice.notFound(response=response, message="No posts found")

	except Exception as e:
		logger.error(e.message, exc_info=True)
		return httpservice.error(response=response, message="There was a problem processing your request")

@route("%s/posts/search/<term>" % config.PUBLIC_API_PREFIX, method="GET")
def getPostCollectionBySearch(term):
	logger = logging.getLogger(__name__)

	try:
		posts, postCount = postservice.searchPosts(searchTerm=term)
		stripper = lambda p: { "title": p["title"], "slug": p["slug"], "publishedYear": p["publishedYear"], "publishedMonth": p["publishedMonth"], "permalink": "/post/{0}/{1}/{2}".format(p["publishedYear"], p["publishedMonth"], p["slug"]) }

		if int(postCount) > 0:
			return {
				"posts": map(stripper, posts),
				"numPosts": int(postCount)
			}
		else:
			return httpservice.notFound(response=response, message="No posts found")

	except Exception as e:
		logger.error(e.message, exc_info=True)
		return httpservice.error(repsonse=response, message="There was a problem processing your request")

@route("%s/posts/tag/<tag>/<page:int>" % config.PUBLIC_API_PREFIX, method="GET")
def getPostCollectionByTag(tag, page):
	logger = logging.getLogger(__name__)

	try:
		posts, postCount, numPages = postservice.getPosts(page=page, status="Published", postsPerPage=config.POSTS_PER_PAGE, tag=tag)

		if int(postCount) > 0:
			return {
				"posts": map(postservice.makePageFriendlyPost, posts),
				"numPages": int(numPages),
				"numPosts": int(postCount)
			}
		else:
			return httpservice.notFound(response=response, message="No posts found")

	except Exception as e:
		logger.error(e.message, exc_info=True)
