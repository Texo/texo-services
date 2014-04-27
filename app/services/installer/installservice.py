#
# File: installerservice.py
# This module provides methods for automating the install of the
# Texo CMS engine. It will setup databases and alter configuration files.
#
# Author:
#    Adam Presley
#

import os
import re
import imp
import config
import database

from bottle import redirect
from services.engine import postservice
from services.identity import userservice
from services.engine import securityservice

#
# Function: isEngineInstalled
# Returns True/False if the engine is setup and installed.
#
def isEngineInstalled():
	return len(config.BLOG_TITLE.strip()) > 0

def setupConfigFile(dbServer, dbName, dbUser, dbPass, blogTitle, postsPerPage, hashKey1, hashKey2, encryptionKey, encryptionIV):
	configContents = _getConfigFileContents()
	configContents = _configReplaceDbSettings(configContents=configContents, dbServer=dbServer, dbName=dbName, dbUser=dbUser, dbPass=dbPass)
	configContents = _configReplaceSessionUrl(configContents=configContents, sessionUrl=_createConnectionString(dbServer=dbServer, dbName=dbName, dbUser=dbUser, dbPass=dbPass))
	configContents = _configReplaceBlogTitle(configContents=configContents, blogTitle=blogTitle)
	configContents = _configReplacePostsPerPage(configContents=configContents, postsPerPage=postsPerPage)
	configContents = _configReplaceSecuritySettings(configContents=configContents, hashKey1=hashKey1, hashKey2=hashKey2, encryptionKey=encryptionKey, encryptionIV=encryptionIV)

	_saveConfigFile(configContents)

def setupDatabase(dbServer, dbPort, dbName, dbUser, dbPass, email, password, firstName, lastName, timezone, hashKey1, hashKey2):
	#
	# TODO: This code is MySQL specific. I would like to
	# support other engines at some point
	#
	database.connect(
		engine   = "mysql",
		host     = dbServer,
		port     = dbPort,
		database = "mysql",
		user     = dbUser,
		password = dbPass
	)

	database.execute("DROP DATABASE IF EXISTS %s;" % dbName)
	database.execute("CREATE DATABASE %s;" % dbName)
	database.execute("USE %s;" % dbName)

	database.execute("""
		CREATE TABLE `settings` (
			`themeName` VARCHAR(50) NOT NULL DEFAULT 'default',
			`timezone` VARCHAR(50) NOT NULL DEFAULT 'UTC'
		) ENGINE=MyISAM;
	""")

	database.execute("""
		CREATE TABLE awssettings (
			accessKeyId VARCHAR(50),
			secretAccessKey VARCHAR(50),
			s3Bucket VARCHAR(100)
		) ENGINE=MyISAM;
	""")

	database.execute("""
		CREATE TABLE `user` (
			`id` INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
			`email` VARCHAR(255) NOT NULL UNIQUE,
			`password` VARCHAR(255) NOT NULL,
			`firstName` VARCHAR(50) NOT NULL,
			`lastName` VARCHAR(50) NOT NULL
		) ENGINE=MyISAM;
	""")

	database.execute("CREATE INDEX `idx_user_email` ON `user` (`email`);")

	database.execute("""
		CREATE TABLE `poststatus` (
			`id` INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
			`status` VARCHAR(20) NOT NULL
		) ENGINE=MyISAM;
	""")

	database.execute("""
		CREATE TABLE `post` (
			`id` INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
			`title` VARCHAR(175) NOT NULL,
			`authorId` INT UNSIGNED NOT NULL,
			`slug` VARCHAR(300) NOT NULL,
			`content` TEXT,
			`createdDateTime` DATETIME,
			`publishedDateTime` DATETIME,
			`publishedYear` INT,
			`publishedMonth` INT,
			`postStatusId` INT UNSIGNED,

			FOREIGN KEY (authorId) REFERENCES user(id),
			FOREIGN KEY (postStatusId) REFERENCES poststatus(id)
		) ENGINE=MyISAM;
	""")

	database.execute("CREATE INDEX `idx_post_publishedDateTime` ON `post` (`publishedDateTime`);")

	database.execute("""
		CREATE TABLE `posttag` (
			`id` INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
			`tag` VARCHAR(20) NOT NULL,
			`howManyTimesUsed` INT NOT NULL DEFAULT 0,

			UNIQUE KEY `posttag_tag` (`tag`)
		) ENGINE=MyISAM;
	""")

	database.execute("CREATE INDEX `idx_posttag_tag` ON `posttag` (`tag`);")

	database.execute("""
		CREATE TABLE `post_posttag` (
			`id` INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
			`postId` INT UNSIGNED NOT NULL,
			`postTagId` INT UNSIGNED NOT NULL,

			UNIQUE KEY `post_posttag_unique_tagandid` (`postId`, `postTagId`),
			FOREIGN KEY (`postId`) REFERENCES post(`id`),
			FOREIGN KEY (`postTagId`) REFERENCES posttag(`id`)
		) ENGINE=MyISAM;
	""")

	database.execute("""
		INSERT INTO settings (themeName, timezone) VALUES
			('default', %s)
		;
	""", (
		timezone,
	))

	database.execute("""
		INSERT INTO user (email, password, firstName, lastName) VALUES
			(%s, %s, %s, %s)
		;
	""", (
		email,
		securityservice.hash(value=password, hashKey1=hashKey1, hashKey2=hashKey2),
		firstName,
		lastName,
	))

	database.execute("""
		INSERT INTO poststatus (status) VALUES
			('Draft'),
			('Published'),
			('Archived')
		;
	""")

	database.execute("""
		INSERT INTO awssettings (accessKeyId, secretAccessKey, s3Bucket) VALUES ('', '', '');
	""")

def _configReplaceBlogTitle(configContents, blogTitle):
	pattern = re.compile(r'(.*?)BLOG_TITLE\s+=\s+"(.*?)"', re.I | re.S)
	result = pattern.sub(r'\1BLOG_TITLE = "' + blogTitle + '"', configContents, count=1)
	return result

def _configReplaceDbSettings(configContents, dbServer, dbName, dbUser, dbPass):
	pattern1 = re.compile(r'(.*?)"DB_HOST":\s+(.*?)"', re.I | re.S)
	pattern2 = re.compile(r'(.*?)"DB_PORT":\s+(.*?),', re.I | re.S)
	pattern3 = re.compile(r'(.*?)"DB_NAME":\s+(.*?)"', re.I | re.S)
	pattern4 = re.compile(r'(.*?)"DB_USER":\s+(.*?)"', re.I | re.S)
	pattern5 = re.compile(r'(.*?)"DB_PASSWORD":\s+(.*?)"', re.I | re.S)

	result = pattern1.sub(r'\1"DB_HOST": "' + dbServer, configContents, count=1)
	result = pattern2.sub(r'\1"DB_PORT": 3306,', result, count=1)
	result = pattern3.sub(r'\1"DB_NAME": "' + dbName, result, count=1)
	result = pattern4.sub(r'\1"DB_USER": "' + dbUser, result, count=1)
	result = pattern5.sub(r'\1"DB_PASSWORD": "' + dbPass, result, count=1)

	return result

def _configReplacePostsPerPage(configContents, postsPerPage):
	pattern = re.compile(r'(.*?)POSTS_PER_PAGE\s+=\s+(.*?)\n', re.I | re.S)
	result = pattern.sub(r'\1POSTS_PER_PAGE = ' + postsPerPage + '\n', configContents, count=1)
	return result

def _configReplaceSecuritySettings(configContents, hashKey1, hashKey2, encryptionKey, encryptionIV):
	pattern1 = re.compile(r'(.*?)HASH_KEY_1\s+=\s+(.*?)\n', re.I | re.S)
	pattern2 = re.compile(r'(.*?)HASH_KEY_2\s+=\s+(.*?)\n', re.I | re.S)
	pattern3 = re.compile(r'(.*?)ENCRYPTION_KEY\s+=\s+(.*?)\n', re.I | re.S)
	pattern4 = re.compile(r'(.*?)ENCRYPTION_IV\s+=\s+(.*?)\n', re.I | re.S)

	result = pattern1.sub(r'\1HASH_KEY_1 = "' + hashKey1 + '"\n', configContents, count=1)
	result = pattern2.sub(r'\1HASH_KEY_2 = "' + hashKey2 + '"\n', result, count=1)
	result = pattern3.sub(r'\1ENCRYPTION_KEY = "' + encryptionKey + '"\n', result, count=1)
	result = pattern4.sub(r'\1ENCRYPTION_IV = "' + encryptionIV + '"\n', result, count=1)

	return result

def _configReplaceSessionUrl(configContents, sessionUrl):
	pattern = re.compile(r'(.*?)"SESSION_URL":\s+"(.*?)"', re.I | re.S)
	result = pattern.sub(r'\1"SESSION_URL": "' + sessionUrl + '"', configContents, count=1)
	return result

def _createConnectionString(dbServer, dbName, dbUser, dbPass):
	return "mysql://%s:%s@%s/%s" % (dbUser, dbPass, dbServer, dbName)

def _getConfigFileContents():
	contents = ""

	with open(os.path.join(config.ROOT_PATH, "config.py"), "r") as f:
		contents = f.read()

	return contents

def _saveConfigFile(configContents):
	with open(os.path.join(config.ROOT_PATH, "config.py"), "w") as f:
		f.write(configContents)
