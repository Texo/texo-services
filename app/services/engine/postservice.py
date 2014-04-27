#
# File: postservice.py
# This module has methods for working with blog posts and any post related data, including tags.
# A post is basically a blog entry, which typically consists of a title, an author, and some
# content. A post may also be associated with one or more *tags*. A tag is simply a type of
# category. Any post may have more than one tag.
#
# It is here in this module you will find what you need to create, modify and archive posts,
# as well as create and update post tags. It also has methods for transforming posts and tags
# into various formats for consumption in Mako templates and JSON.
#
# Author:
#    Adam Presley
#
import math
import uuid
import config
import database
import markdown

from services.datetimehelper import dthelper


#
# Function: getAllPosts
# Returns all posts.
#
def getAllPosts():
	return _getPosts()

#
# Function: archivePost
# This function archives a post by setting its status to Archived.
# Returns the number of affected rows.
#
# Parameters:
#    postId - Post ID
#
def archivePost(postId):
	database.execute(sql="""
		UPDATE post SET
			postStatusId=(SELECT id FROM poststatus WHERE status='Archived' LIMIT 1)
		WHERE id=%s
	""", parameters=(
		postId,
	))

	return database.LAST_NUM_AFFECTED

#
# Function: calcPageStartEnd
# Calculates start and end records based on a page number. This
# is used in paging to determine what database records to retrieve.
# Returns a tuple of *(start, end)* for the start/end record numbers.
#
# Parameters:
#    page         - Page number
#    postsPerPage - Number of posts displayed per page
#
# Example:
#    (start code)
#    from services.engine import postservice
#
#    start, end = postservice.calcPageStartEnd(page=2, postsPerPage=10)
#    # start == 10
#    # end == 20
#    (end)
#
def calcPageStartEnd(page, postsPerPage):
	start = (int(page) - 1) * postsPerPage
	end = start + postsPerPage

	return (start, end)

#
# Function: createPost
# Creates a new post in the database. Once the post itself is created this method
# calls <createUpdatePostTags()> to create any tags that do not exist, or update existing
# tags. A dictionary containing this post's information is returned in the event of success.
#
# Parameters:
#    title             - Title of this post. *Required*
#    author            - A user dictionary representing the author of this post. *Required*
#    slug              - URL-slug for this post. *Required*
#    content           - Markdown-formatted blog post content. *Required*
#    createdDateTime   - Date/time created. *Required*
#    tags              - List of tags. Can be a comma-delimited string, or an arrray/tuple of strings. *Required*
#    status            - A Status dictionary. *Required*
#    publishedDateTime - Date/time post has been published.
#    publishedYear     - Year of publication
#    publishedMonth    - Month of publication
#
# Example:
#    (start code)
#    from services.engine import postservice
#
#    newPost = postservice.createPost(
#       title                = "Test",
#       author               = request.all["user"],
#       slug                 = "test-post",
#       content              = "This is test content and stuff.",
#       createdDateTime      = dthelper.utcnow(),
#       tags                 = "test,post",
#       status               = "Draft"
#    )
#    (end)
#
def createPost(title, author, slug, content, createdDateTime, tags, status, publishedDateTime=None, publishedYear=None, publishedMonth=None):
	if len(title) < 3: return (False, "Title must be at least 3 characters", None)
	if len(slug) < 3: return (False, "Slug must be at least 3 characters", None)
	if len(content) < 3: return (False, "Content must be at least 3 characters", None)

	if isinstance(tags, basestring):
		tags = tags.split(",")

	id = database.execute(sql="""
		INSERT INTO post (
			  title
			, authorId
			, slug
			, content
			, createdDateTime
			, postStatusId
			, publishedDateTime
			, publishedYear
			, publishedMonth
		) VALUES (
			  %s
			, %s
			, %s
			, %s
			, %s
			, %s
			, %s
			, %s
			, %s
		)
	""", parameters=(
		  title
		, author["id"]
		, slug
		, content
		, dthelper.formatDateTime(date=createdDateTime)
		, status["id"]
		, None if publishedDateTime is None else dthelper.formatDateTime(date=publishedDateTime)
		, None if publishedYear is None else dthelper.getYear(date=publishedYear)
		, None if publishedMonth is None else dthelper.getMonth(date=publishedMonth)
	))

	createUpdatePostTags(postId=id, tags=tags)

	return newPostBean(
		title            = title,
		authorId         = author["id"],
		slug             = slug,
		content          = content,
		createdDateTime  = dthelper.parseDateTime(date=createdDateTime),
		publishedDateTime= None if publishedDateTime is None else dthelper.parseDateTime(date=publishedDateTime),
		publishedYear    = None if publishedYear is None else dthelper.getYear(date=publishedYear),
		publishedMonth   = None if publishedMonth is None else dthelper.getMonth(date=publishedMonth),
		postStatusId     = status["id"],
		tags             = tags,
	)

#
# Function: createPostStatus
# Creates a new post status. This is not typically called directly expect by the setup process.
#
# Parameters:
#    status - Name of the new status to create
#
# Returns:
#    A new status bean
#
def createPostStatus(status):
	id = database.execute(sql="""
		INSERT INTO poststatus (
			status
		) VALUES (
			%s
		)
	""", parameters=(
		status,
	))

	return newPostStatusBean(id=id, status=status)

#
# Function: createUpdatePostTags
# Tags an array of tag strings and performs the following logic against each tag:
#    * Creates the tag if it does not exist
#    * Updates the use count on a tag if it does exist
#    * Creates the association between tag and post
#
# Parameters:
#    tags - Array of strings, each string being a post tag
#
def createUpdatePostTags(postId, tags):
	createTagSql = """
		INSERT INTO posttag (
			  tag
			, howManyTimesUsed
		) VALUES
	"""

	createLinkSql = """
		INSERT INTO post_posttag (postId, postTagId)
		SELECT %s, id FROM posttag WHERE tag IN (
	"""

	createTagParameters = []
	createLinkParameters = [int(postId)]

	for index, tagName in enumerate(tags):
		createTagSql += " (%s, 1)"
		createLinkSql += "%s"

		if index < len(tags) - 1:
			createTagSql += ","
			createLinkSql += ", "

		createTagParameters.append(tagName)
		createLinkParameters.append(tagName)

	createTagSql += " ON DUPLICATE KEY UPDATE howManyTimesUsed = howManyTimesUsed + 1"
	createLinkSql += ") ON DUPLICATE KEY UPDATE postTagId = VALUES(postTagId)"

	createTagParameters = tuple(createTagParameters)
	createLinkParameters = tuple(createLinkParameters)

	#
	# First create any new tags or update usage counts for existing tags.
	#
	database.execute(sql=createTagSql, parameters=createTagParameters)

	#
	# Next delete post -> tag association records that are no longer
	# needed.
	#
	deleteUnusedPostTags(postId=postId, tagsToKeep=tags)

	#
	# Create any new post -> tag association records.
	#
	database.execute(sql=createLinkSql, parameters=createLinkParameters)

#
# Function: deleteAllPosts
# This method deletes all posts and directly related data, such as tags.
# WARNING: This is a dangerous function an should be called only
# where really intended.
#
def deleteAllPosts():
	database.execute(sql="DELETE FROM post_posttag")
	database.execute(sql="DELETE FROM posttag")
	database.execute(sql="DELETE FROM post")

#
# Function: deletePost
# This method deletes a post by ID. It also delete related post
# tags.
#
# Parameters:
#    postId - ID of a post
#
def deletePost(postId):
	database.execute(sql="""
		DELETE FROM post_posttag
		WHERE postId=%s
	""", parameters=(postId,))

	database.execute(sql="""
		DELETE FROM post
		WHERE id=%s
	""", parameters=(postId,))

#
# Function: deleteUnusedPostTags
# Deletes any unused tags for a specified post and set of tags that should be
# kept.
#
# Parameters:
#    postId - ID of a post
#    tagsToKeep - Array of tag names to keep associated to this post
#
def deleteUnusedPostTags(postId, tagsToKeep):
	tableName = "tagstodelete{0}".format(uuid.uuid4().hex)

	database.execute(sql="""
		CREATE TEMPORARY TABLE {tablename} (
			id INT UNSIGNED,
			tag VARCHAR(20)
		);
	""".format(
		tablename=tableName
	))

	database.execute(sql="""
		INSERT INTO {tablename} (id, tag)
		SELECT posttag.id, posttag.tag
		FROM post_posttag
			JOIN posttag ON posttag.id=post_posttag.postTagId
		WHERE
			post_posttag.postId={postId}
			AND posttag.tag NOT IN ({tagPlaceholders})
		;
	""".format(
		tablename=tableName,
		postId=postId,
		tagPlaceholders=", ".join(["%s" for t in tagsToKeep]),
	), parameters=tuple(tagsToKeep))

	database.execute(sql="""
		DELETE post_posttag FROM post_posttag
		JOIN {tablename} ON {tablename}.id=post_posttag.postTagId
		WHERE
			postId=%s
		;
	""".format(
		tablename=tableName,
	), parameters=(postId,))

	database.execute(sql="""
		UPDATE posttag SET
			howManyTimesUsed = howManyTimesUsed - 1
		WHERE
			id=(SELECT id FROM {tablename})
		;
	""".format(
		tablename=tableName,
	))

	database.execute(sql="""
		DROP TABLE {tablename};
	""".format(
		tablename=tableName,
	))

#
# Function: filterPostsByStatus
# Returns posts that match a status. See <POST_STATUSES> for the available
# status options.
#
# Parameters:
#    posts - List of post objects containing blog post data
#    status - Status to filter posts by. Defaults to None
#
# Returns:
#    Filtered list of posts
#
def filterPostsByStatus(posts, status=None):
	return posts if status is None else filter(lambda post: post["status"] == status, posts)

#
# Function: filterPostsByTag
# Returns posts that match a tag. Posts can be labelled with one or more
# tags. This function will return all posts that contain the specified
# tag.
#
# Parameters:
#    posts - List of post objects containing blog post data
#    tag - Tag (string) to filter posts by. Defaults to None
#
# Returns:
#    Filtered list of posts
#
def filterPostsByTag(posts, tag=None):
	results = posts

	if tag is not None:
		tagObject = posttag.getTagByName(tag)
		results = [post for post in posts if tagObject in post.tags]

	return results

#
# Function: getAllPublishedPosts
# Retrieves all Published posts.
#
# Returns:
#    A list of Post objects
#
def getAllPublishedPosts():
	allPosts = sortPosts(getAllPosts())
	posts = filterPostsByStatus(posts=allPosts, status="Published")

	return posts

#
# Function: getPostByDateAndSlug
# This function attempts to retrieve a single post by its published date
# and URL-slug. Only the year and month of the published date is required.
# If a matching post is found the post dictionary is returned. Otherwise None
# is returned.
#
#    > {
#    >   "id": 0,
#    >   "title": "Title",
#    >   "authorId": 0,
#    >   "author": "Adam Presley",
#    >   "slug": "title-is-here",
#    >   "content": "This is content yo",
#    >   "createdDateTime": "2014-01-01 00:00:00",
#    >   "publishedDateTime": "2014-01-01 00:01:00",
#    >   "publishedYear": 2014,
#    >   "publishedMonth": 1,
#    >   "postStatusId": 1,
#    >   "status": "Published",
#    >   "tagList": "Test,Stuff",
#    >   "tagIdList": "1,2"
#    > }
#
# Parameters:
#    year  - Published year
#    month - Published month
#    slug  - URL-slug for this post
#
def getPostByDateAndSlug(year, month, slug):
	post = _getPosts(status="Published", year=year, month=month, slug=slug)
	return None if len(post) <= 0 else post[0]

#
# Function: getPostById
# Retrieve and return a single blog post by ID.
#
# Parameteres:
#    id - ObjectID of the post to retrieve
#
# Returns:
#    A post object
#
def getPostById(id):
	posts = _getPosts(id=id)
	return None if len(posts) <= 0 else posts[0]

#
# Function: getPosts
# Retrieves a list of posts matching a set of criteria. This function
# is generally used to return a page worth of posts and is potentially filtered
# by status and/or tag. This function makes use of <filterPostsByStatus>
# and <filterPostsByTag>.
#
# This returns a tuple of posts, number of posts, and number of pages
#
# Parameters:
#    page - Page number of posts to retrieve. Defaults to 1
#    status - Status to filter posts by. Defaults to None
#    tag - Tag to filter posts by. Defaults to None
#    postsPerPage - Number of posts per page. Defaults to 5
#
def getPosts(page=1, status=None, tag=None, postsPerPage=5):
	start, end = calcPageStartEnd(page=page, postsPerPage=postsPerPage)
	posts = _getPosts(status=status, tag=tag)

	postCount = len(posts)

	if page > 0:
		posts = posts[start:end]

	numPages = math.ceil(float(postCount) / float(postsPerPage))

	return (posts, postCount, numPages)

#
# Function: getPostStatus
# Retrieves a PostStatus object by status name. For example
#
#    (start code)
#    postStatus = postservice.getPostStatus(status="Published")
#    # postStatus == { "id": 1, "status": "Published" }
#    (end)
#
# Parameters:
#    status - Name of the status to retrieve
#
def getPostStatus(status):
	statuses = database.query(sql="""
		SELECT
			  id
			, status
		FROM poststatus
		WHERE 1=1
			AND status=%s
	""", parameters=(
		status,
	))

	return None if not statuses else statuses[0]

#
# Function: getPostTagById
# Returns a post tag by ID
#
def getPostTagById(id):
	tag = database.query(sql="""
		SELECT
			  posttag.id
			, posttag.tag
			, posttag.howManyTimesUsed

		FROM posttag
		WHERE
			posttag.id=%s
	""", parameters=(
		id,
	))

	return None if not tag else tag[0]

#
# Function: getPostTags
# Returns a tuple of post tags.
#
def getPostTags():
	tags = database.query(sql="""
		SELECT
			  posttag.id
			, posttag.tag
			, posttag.howManyTimesUsed

		FROM posttag
		WHERE
			posttag.howManyTimesUsed > 0
		ORDER BY
			posttag.howManyTimesUsed DESC
	""")

	return map(makeFriendlyTag, tags)

#
# Function: makeFriendlyTag
# Takes a tag record and returns a a friendly tag. This basically
# adds some additional information to the tag, such as a single-tag
# JSON url, and a URL for posts-by-tag.
#
# Parameters:
#    tag
#
def makeFriendlyTag(tag):
	return {
		"id"              : tag["id"],
		"tag"             : tag["tag"],
		"howManyTimesUsed": tag["howManyTimesUsed"],
		"getTagUrl"       : "%s/tag/%s" % (config.PUBLIC_API_PREFIX, tag["id"],),
		"getPostsByTagUrl": "/posts/%s" % tag["tag"],
	}

#
# Function: makePageFriendlyPost
# Takes a post record and returns a page-friendly dictionary. "Page-friendly"
# basically means giving various date/time formats for display, arrays of tags
# and tag IDs.
#
# Parameters:
#    post - A post dictionary
#
def makePageFriendlyPost(post):
	tz = lambda d: dthelper.utcToTimezone(targetTimezone=config.TIMEZONE, date=d)
	parseFormat = "%Y-%m-%d %H:%M:%S%z"

	return {
		"id"                   : post["id"],
		"title"                : post["title"],
		"authorId"             : post["authorId"],
		"author"               : post["author"],
		"slug"                 : post["slug"],
		"permalink"            : "/post/{0}/{1}/{2}".format(post["publishedYear"], post["publishedMonth"], post["slug"]),
		"rawContent"           : post["content"],
		"renderedContent"      : renderMarkdown(rawMarkdown=post["content"]),
		"createdDateTime"      : dthelper.formatDateTime(date=tz(post["createdDateTime"]), parseFormat=parseFormat),
		"publishedDateTime"    : "" if post["publishedDateTime"] == None else dthelper.formatDateTime(date=tz(post["publishedDateTime"]), parseFormat=parseFormat),
		"publishedDate"        : "" if post["publishedDateTime"] == None else dthelper.formatDate(date=tz(post["publishedDateTime"]), parseFormat=parseFormat),
		"publishedDateUSFormat": "" if post["publishedDateTime"] == None else dthelper.formatDate(date=tz(post["publishedDateTime"]), outputFormat="%m/%d/%Y", parseFormat=parseFormat),
		"publishedTime"        : "" if post["publishedDateTime"] == None else dthelper.formatTime(date=tz(post["publishedDateTime"]), parseFormat=parseFormat),
		"publishedTime12Hour"  : "" if post["publishedDateTime"] == None else dthelper.formatTime(date=tz(post["publishedDateTime"]), outputFormat="%I:%M %p", parseFormat=parseFormat),
		"publishedYear"        : post["publishedYear"],
		"publishedMonth"       : post["publishedMonth"],
		"postStatusId"         : post["postStatusId"],
		"status"               : post["status"],
		"tagList"              : post["tagList"],
		"tags"                 : "" if not post["tagList"] else post["tagList"].split(","),
		"tagIdList"            : post["tagIdList"],
		"tagIds"               : "" if not post["tagIdList"] else post["tagIdList"].split(","),
	}

#
# Function: newPostBean
# Returns a new dictionary representing a post.
#
def newPostBean(title="", authorId=0, slug="", content="", createdDateTime=None, publishedDateTime=None, publishedYear=0, publishedMonth=0, postStatusId=0, tags=[]):
	return {
		"title"            : title,
		"authorId"         : authorId,
		"slug"             : slug,
		"content"          : content,
		"createdDateTime"  : createdDateTime,
		"publishedDateTime": publishedDateTime,
		"publishedYear"    : publishedYear,
		"publishedMonth"   : publishedMonth,
		"postStatusId"     : postStatusId,
		"tags"             : tags,
	}

#
# Function: newPostStatusBean
# Returns a new dictionary representing a post status.
#
def newPostStatusBean(id=0, status=""):
	"""Creates a post status dictionary object"""

	return {
		"id"    : id,
		"status": status,
	}

#
# Function: parseMarkdownFile
# Parses a markdown file and returns information suitable for
# inserting as a new post. Returns:
#    * metadata - Blog info, such as title and tags
#    * content
#
# Parameters:
#    fileName - Full path to the Markdown file to process
#
def parseMarkdownFile(fileName, sourceTimezone):
	with open(fileName) as markdownFile:
		markdownContent = markdownFile.read()

	#
	# Parse the file
	#
	mode = "METADATA"
	metadata = {}
	content = []

	for line in markdownContent.split("\n"):
		if mode == "METADATA":
			if line.find(":") == -1:
				mode = "CONTENT"

				if len(line.strip()):
					content.append(line)
			else:
				split = line.split(":")
				key = split[0].strip().lower()

				if key == "tags":
					value = [tag.strip() for tag in split[1].split(",")]
				elif key == "date":
					value = "{0}:{1}".format(split[1], split[2]).strip()
					value = dthelper.formatDateTime(date=dthelper.timezoneToUtc(sourceTimezone=sourceTimezone, date=value, parseFormat="%Y-%m-%d %H:%M"), parseFormat="%Y-%m-%d %H:%M:%S%z")

					metadata["publishedMonth"] = int(dthelper.getMonth(date=value, parseFormat=dthelper.REST_DATETIME_FORMAT))
					metadata["publishedYear"] = int(dthelper.getYear(date=value, parseFormat=dthelper.REST_DATETIME_FORMAT))

				else:
					value = ":".join(split[1:]).strip()

				metadata[key] = value
		else:
			content.append(line)

	return (metadata, stipInvalidUnicodeCharacters("\n".join(content)))

#
# Function: publishPost
# This function published a post by setting it's status to Published,
# as well as updating published dates if they were previously null.
# Returns the number of affected rows.
#
# Parameters:
#    postId - Post ID
#
def publishPost(postId):
	database.execute(sql="""
		UPDATE post SET
			  postStatusId=(SELECT id FROM poststatus WHERE status='Published' LIMIT 1)
			, publishedDateTime=CASE
				WHEN publishedDateTime IS NULL THEN %s
				ELSE publishedDateTime
			END
			, publishedYear=CASE
				WHEN publishedYear IS NULL THEN %s
				ELSE publishedYear
			END
			, publishedMonth=CASE
				WHEN publishedMonth IS NULL THEN %s
				ELSE publishedMonth
			END
		WHERE id=%s
	""", parameters=(
		dthelper.formatDateTime(date=dthelper.utcNow()),
		dthelper.getYear(date=dthelper.utcNow()),
		dthelper.getMonth(date=dthelper.utcNow()),
		postId,
	))

	return database.LAST_NUM_AFFECTED


#
# Function: rawPostToJson
# Constructs a dictionary containing post information, formatted dates,
# and raw Markdown content.
#
# Parameters:
#    post - Post object
#
# Returns:
#    Dictionary of post data. Looks like this.
#
#    > {
#    >    "id": 1,
#    >    "title": "Blog Post",
#    >    "author": "Adam Presley",
#    >    "slug": "blog-post",
#    >    "publishedDate": "2013-01-01",
#    >    "publishedDateTime": "2013-01-01 13:00",
#    >    "year": 2013,
#    >    "month": 1,
#    >    "tags": "test,stuff,tag",
#    >    "content": "This is **markdown** content",
#    >    "status": "Draft"
#    > }
#
def rawPostToJson(post):
	return {
		"id": str(post.id),
		"title": post.title,
		"author": "{0} {1}".format(post.author.firstName, post.author.lastName),
		"slug": post.slug,
		"publishedDate": None if "publishedDate" not in post else datetime.strftime(post.publishedDate, "%Y-%m-%d"),
		"publishedDateTime": None if "publishedDateTime" not in post else datetime.strftime(post.publishedDateTime, "%Y-%m-%d %H:%M"),
		"year": None if "publishedDate" not in post else datetime.strftime(post.publishedDate, "%Y"),
		"month": None if "publishedDate" not in post else datetime.strftime(post.publishedDate, "%m"),
		"tags": ",".join([tag.tag for tag in post.tags]),
		"content": post.content,
		"status": post.status
	}

#
# Function: renderPostToJson
# Constructs a dictionary containing post information, formatted dates,
# and rendered Markdown content.
#
# Parameters:
#    post - Post object
#
# Returns:
#    Dictionary of post data. Looks like this.
#
#    > {
#    >    "id": 1,
#    >    "title": "Blog Post",
#    >    "author": "Adam Presley",
#    >    "slug": "blog-post",
#    >    "publishedDate": "2013-01-01",
#    >    "publishedDateTime": "2013-01-01 13:00",
#    >    "year": 2013,
#    >    "month": 1,
#    >    "tags": ["test", "stuff", "tag"],
#    >    "content": "This is <strong>markdown</strong> content",
#    >    "status": "Published"
#    > }
#
def renderPostToJson(post):
	return {
		"id": str(post.id),
		"title": post.title,
		"author": "{0} {1}".format(post.author.firstName, post.author.lastName),
		"slug": post.slug,
		"publishedDate": None if "publishedDate" not in post else datetime.strftime(post.publishedDate, "%Y-%m-%d"),
		"publishedDateTime": None if "publishedDateTime" not in post else datetime.strftime(post.publishedDateTime, "%Y-%m-%d %H:%M"),
		"year": None if "publishedDate" not in post else datetime.strftime(post.publishedDate, "%Y"),
		"month": None if "publishedDate" not in post else datetime.strftime(post.publishedDate, "%m"),
		"tags": [tag.tag for tag in post.tags],
		"content": self.renderMarkdown(rawMarkdown=post.content),
		"status": post.status
	}

#
# Function: renderMarkdown
# This function makes use of the Python Markdown extension to render markdown
# content into HTML. Currently it is setup with the following extensions.
#
#    * codehilite
#    * tables
#    * extra
#
# Parameters:
#    rawMarkdown - String of raw markdown text
#
# Returns:
#    A string of markdown rendered to HTML
#
def renderMarkdown(rawMarkdown):
	extensions = [
		"codehilite(css_class=highlight",
		"tables",
		"extra",
	]

	if config.CODE_LINE_NUMBERS:
		extensions[0] = extensions[0] + ",linenums=True)"
	else:
		extensions[0] = extensions[0] + ")"

	return markdown.markdown(rawMarkdown.decode("utf-8"), output_format="html5", extensions=extensions)

#
# Function: searchPosts
# Retrieves a list of posts matching a set of seach criteria. This function
# is generally used by a search function in the application.
#
# This returns a tuple of posts, number of posts
#
# Parameters:
#    searchTerm - Term to search by
#
def searchPosts(searchTerm):
	posts = _getPosts(status="Published", searchTerm=searchTerm)
	postCount = len(posts)

	return (posts, postCount)

#
# Function: stipInvalidUnicodeCharacters
# Removes Unicode characters that exceed a certain ordinal range.
#
def stipInvalidUnicodeCharacters(content):
	result = content

	if type(result) is unicode:
		result = "".join([x for x in result if ord(x) < 128])

	return result

#
# Function: updatePost
# Updates an existing post in the database.
#
# Parameters:
#    id - ID of the post to update
#    title - Title of this post
#    slug - URL-slug for this post
#    content - Markdown content
#    tags - List of tag objects
#    status - Status of this post
#    publishedDate - Date post has been published
#    publishedDateTime - Date/time post has been published
#    publishedYear - Year of publication
#    publishedMonth - Month of publication
#
# Returns:
#    Existing post object
#
def updatePost(id, title, slug, content, tags, status, publishedDateTime=None, publishedYear=None, publishedMonth=None):
	if len(title) < 3: return (False, "Title must be at least 3 characters", None)
	if len(slug) < 3: return (False, "Slug must be at least 3 characters", None)
	if len(content) < 3: return (False, "Content must be at least 3 characters", None)

	post = getPostById(id=id)
	tags = tags.split(",")

	if post:
		post["title"] = title
		post["slug"] = slug
		post["content"] = content
		post["tags"] = tags
		post["status"] = status
		post["postStatusId"] = getPostStatus(status=status)["id"]
		post["publishedDateTime"] = None if publishedDateTime is None else dthelper.formatDateTime(date=publishedDateTime)
		post["publishedYear"] = None if publishedYear is None else dthelper.getYear(date=publishedYear)
		post["publishedMonth"] = None if publishedMonth is None else dthelper.getMonth(date=publishedMonth)

		sql = """
			UPDATE post SET
				  title=%s
				, slug=%s
				, content=%s
				, publishedDateTime=%s
				, publishedYear=%s
				, publishedMonth=%s
				, postStatusId=%s
			WHERE id=%s
		"""

		parameters = (
			post["title"],
			post["slug"],
			post["content"],
			post["publishedDateTime"],
			post["publishedYear"],
			post["publishedMonth"],
			post["postStatusId"],
			id,
		)

		database.execute(sql=sql, parameters=parameters)
		createUpdatePostTags(postId=id, tags=post["tags"])

	return post


###############################################################################
# Private methods
###############################################################################

def _getPosts(id=None, status=None, tag=None, year=None, month=None, slug=None, searchTerm=None):
	parameters = []

	sql = """
		SELECT
			  post.id
			, post.title
			, post.authorId
			, CONCAT(user.firstName, ' ', user.lastName) AS author
			, post.slug
			, post.content
			, post.createdDateTime
			, post.publishedDateTime
			, post.publishedYear
			, post.publishedMonth
			, post.postStatusId
			, poststatus.status AS status
			, (
				SELECT GROUP_CONCAT(posttag.tag SEPARATOR ',')
				FROM post_posttag
					INNER JOIN posttag ON posttag.id=post_posttag.postTagId
				WHERE
					post_posttag.postId=post.id
			) AS tagList
			, (
				SELECT GROUP_CONCAT(posttag.id SEPARATOR ',')
				FROM post_posttag
					INNER JOIN posttag ON posttag.id=post_posttag.postTagId
				WHERE
					post_posttag.postId=post.id
			) AS tagIdList

		FROM post
			INNER JOIN user ON user.id=post.authorId
			INNER JOIN poststatus ON poststatus.id=post.postStatusId

		WHERE 1=1
	"""

	if id:
		parameters.append(id)
		sql += " AND post.id=%s"

	if status:
		parameters.append(status)
		sql += " AND poststatus.status=%s"

	if tag:
		parameters.append(tag)
		sql += """
			AND (
				SELECT COUNT(post_posttag.postId)
				FROM post_posttag
					INNER JOIN posttag ON posttag.id=post_posttag.postTagId
				WHERE
					post_posttag.postId=post.id
					AND posttag.tag=%s
			) > 0
		"""

	if year:
		parameters.append(year)
		sql += " AND post.publishedYear=%s"

	if month:
		parameters.append(month)
		sql += " AND post.publishedMonth=%s"

	if slug:
		parameters.append(slug)
		sql += " AND post.slug=%s"

	if searchTerm:
		parameters.append("%%%s%%" % searchTerm)
		parameters.append("%%%s%%" % searchTerm)

		sql += """
			AND (
				post.title LIKE %s
				OR post.content LIKE %s
			)
		"""

	sql += """
		ORDER BY
			post.createdDateTime DESC
	"""

	qryPosts = database.query(sql=sql, parameters=tuple(parameters))
	return qryPosts
