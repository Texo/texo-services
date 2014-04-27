import MySQLdb as mysql
import logging

ENGINE = "mysql"
DB = None

LAST_NUM_AFFECTED = 0
LAST_RECORD_COUNT = 0

def connect(engine, host, port, database, user, password):
	global DB
	global ENGINE

	ENGINE = engine

	try:
		if engine == "mysql":
			DB = mysql.connect(host=host, port=port, user=user, passwd=password, db=database)

	except Exception as e:
		logger = logging.getLogger(__name__)
		logger.error(e.message)

def disconnect():
	global DB

	if DB:
		DB.close()

def execute(sql, parameters=None, commit=True):
	global DB
	global LAST_NUM_AFFECTED

	logger = logging.getLogger(__name__)
	cursor = DB.cursor()

	cursor.execute(sql, args=parameters)
	LAST_NUM_AFFECTED = cursor.rowcount

	if commit:
		DB.commit()
		return cursor.lastrowid

	return None

def query(sql, parameters=None, fetchAll=True):
	global DB
	global LAST_RECORD_COUNT

	logger = logging.getLogger(__name__)
	cursor = DB.cursor(mysql.cursors.DictCursor)

	cursor.execute(sql, args=parameters)
	LAST_RECORD_COUNT = cursor.rowcount

	if fetchAll:
		results = cursor.fetchall()
		cursor.close()

		return results
	else:
		return cursor