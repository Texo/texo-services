import os

#
# Blog Settings
# Configure the specifics of your blog here.
#
BLOG_TITLE = "Adam.Blog()"
BLOG_TAGLINE = ""
POSTS_PER_PAGE = 5
CODE_LINE_NUMBERS = False

HASH_KEY_1 = "12345"
HASH_KEY_2 = "54321"
ENCRYPTION_KEY = "key"
ENCRYPTION_IV = "salt"



#
# Environment Configuration
# The primary changes you would make here would be
# the ENV variable, as well as the specific
# environment settings, such as port and IP bindings.
#
ROOT_PATH          = os.path.abspath(os.path.dirname(__file__))
APP_PATH           = ROOT_PATH
WWW_PATH           = os.path.join(APP_PATH, "www")
CONTROLLER_PATH    = os.path.join(WWW_PATH, "controllers")
STATIC_PATH        = os.path.join(WWW_PATH, "static")
BASE_TEMPLATE_PATH = os.path.join(WWW_PATH, "views")
THEME_PATH         = os.path.join(WWW_PATH, "themes")
SESSION_PATH       = os.path.join(WWW_PATH, "sessions")
UPLOAD_PATH        = os.path.join(WWW_PATH, "uploads")
TIMEZONE           = "UTC"

PUBLIC_API_PREFIX  = "/v1/rest"
ADMIN_API_PREFIX   = "/v1/api"

ENVIRONMENT = {
	"DOMAIN": "localhost",
	"BIND_TO_HOST": "localhost",
	"BIND_TO_PORT": 9090,
	"SESSION_URL": "mysql://root:password@localhost/texocms",
	"DB_HOST": "localhost",
	"DB_NAME": "texocms",
	"DB_PORT": 3306,
	"DB_USER": "root",
	"DB_PASSWORD": "password",
	"PROCESS_NAME": "texocms",
	"PIDFILE": "texocms-pid",
	"NUM_WORKER_PROCESSES": 4,
}

SESSION_OPTS = {
	"session.type"          : "ext:database",
	"session.url"           : ENVIRONMENT["SESSION_URL"],
	"session.cookie_expires": 14400,
	"session.auto"          : True,
	"session.lock_dir"      : os.path.join(SESSION_PATH, "lock"),
}

CACHE_OPTS = {
	"cache.type"    : "ext:database",
	"cache.url"     : ENVIRONMENT["SESSION_URL"],
	"cache.lock_dir": os.path.join(SESSION_PATH, "lock"),
}