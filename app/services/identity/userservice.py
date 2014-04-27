#
# File: userservice.py
# This module provides a set of functions for working with users and user sessions.
# A user is an entity in the software that has access to create and modify settings,
# blog entries, and more.
#
# Sessions have very few assumptions, and a session object must be passed to each
# method that works with them. This module does assume that the session implementation
# supports working as a dictionary, and has a method named *save()* which persists
# the session object to whatever backing medium it is configured to use.
#
# Author:
#    Adam Presley
#
import database

from services.engine import securityservice
from validate_email import validate_email

###############################################################################
# Section: Module Variables
###############################################################################

# Constant: MAX_EMAIL_LENGTH
# Maximum length of an email address: *255*
MAX_EMAIL_LENGTH = 255

# Constant: MAX_PASSWORD_LENGTH
# Maximum length of a user password: *128*
MAX_PASSWORD_LENGTH = 128



#
# Function: createUser
# Creates a new user in the database
#
# Parameters:
#    email - User's email address. Email address is used to log in to the system
#    password - User's password
#    firstName - User's first name
#    lastName - User's last name
#
# Returns:
#    A new user dictionary
#
def createUser(email, password, firstName, lastName):
	hashedPassword = securityservice.hash(value=password)

	id = database.execute(sql="""
		INSERT INTO user (
			  email
			, password
			, firstName
			, lastName
		) VALUES (
			  %s
			, %s
			, %s
			, %s
		)
	""", parameters=(
		email,
		hashedPassword,
		firstName,
		lastName,
	))

	return newUserBean(
		id        = id,
		email     = email,
		password  = hashedPassword,
		firstName = firstName,
		lastName  = lastName
	)

#
# Function: deleteUserFromSession
# Removes a user's information from a session object.
#
# Parameters:
#    session - A session object
#
def deleteUserFromSession(session):
	if userInSession(session=session):
		session.pop("user", None)

#
# Function: getUserByEmail
# Retrieves a user object by email address. If a user is not found by
# that email address None is returned.
#
# Parameters:
#    email - Email address of the user object ot retrieve
#
# Returns:
#    A matching user object or None if one is not found
#
def getUserByEmail(email):
	qryUser = database.query(sql="""
		SELECT
			id
			, email
			, firstName
			, lastName
			, password

		FROM user
		WHERE 1=1
			AND email=%s
	""", parameters=(
		email,
	))

	if len(qryUser) > 0:
		return qryUser[0]
	else:
		return None

#
# Function: getUserById
# Retrieves a user object by ID. If a user is not found
# then None is returned. Returns a record that contain:
#
#     > {
#     >   "id": 0,
#     >   "email": "555@555.com",
#     >   "firstName": "Adam",
#     >   "lastName": "Presley",
#     >   "password": "12345"
#     > }
#
#
# Parameters:
#    id - ObjectID of the user to retrieve
#
def getUserById(id):
	qryUser = database.query(sql="""
		SELECT
			id
			, email
			, firstName
			, lastName
			, password

		FROM user
		WHERE 1=1
			AND id=%s
	""", parameters=(
		id,
	))

	if len(qryUser) > 0:
		return qryUser[0]
	else:
		return None

#
# Function: getUsersByName
# Retrieves a set of users that match a first name and last name. This can return
# more than one result. Returns records that contain:
#
#     > {
#     >   "id": 0,
#     >   "email": "555@555.com",
#     >   "firstName": "Adam",
#     >   "lastName": "Presley"
#     > }
#
# Parameters:
#    firstName - User's first name
#    lastName  - User's last name
#
def getUsersByName(firstName, lastName):
	users = database.query(sql="""
		SELECT
			  id
			, email
			, firstName
			, lastName
		FROM user
		WHERE 1=1
			AND firstName=%s
			AND lastName=%s
	""", parameters=(
		firstName,
		lastName,
	))

	return users

#
# Function: isCorrectUserPassword
# Compares a password to the password found on a user record
# and returns true/false if the password matches.
#
# Parameters:
#    user - User object
#    password - Password you wish to verify
#
# Returns:
#    A tuple of the following: True/False if the password matches and any error message.
#    Error message will be None if there is no error
#
def isCorrectUserPassword(user, password):
	try:
		salt = securityservice.extractSaltFromPassword(password=user["password"])
		hashedPassword = securityservice.hash(value=password, salt=salt)

		if user["password"] != hashedPassword:
			return (False, None)

	except Exception as e:
		return (False, e.message)

	return (True, None)

#
# Function: isUserEmailValid
# Returns True/False if the provided user email address is
# valid or not.
#
# Parameters:
#    email - Email address to verify
#
# Returns:
#    True/False if the provided email address is valid user email
#    address or not. This function verifies length and form.
#
def isUserEmailValid(email):
	if len(email) > MAX_EMAIL_LENGTH or len(email.strip()) <= 0:
		return False

	if not validate_email(email):
		return False

	return True

#
# Function: isUserPasswordValid
# Returns True/False if the provided user password is valid or not.
#
# Parameters:
#    password - The cleartext password to verify
#
# Returns:
#    True/False if the provided user password is valid or not.
#    This validates length
#
def isUserPasswordValid(password):
	if len(password) > MAX_PASSWORD_LENGTH or len(password.strip()) <= 0:
		return False

	return True

#
# Function: newUserBean
# Creates a user dictionary
#
# Parameters:
#    id - User ID. Defaults 0
#    email - Email address. Defaults to ""
#    password - Password. Defaults to ""
#    firstName - First name of the user. Defaults to ""
#    lastName - Last name of the user. Defaults to ""
#
# Returns:
#    A dictionary of user information
#
def newUserBean(id=0, email="", password="", firstName="", lastName=""):
	return {
		"id"       : id,
		"email"    : email,
		"password" : password,
		"firstName": firstName,
		"lastName" : lastName,
	}

#
# Function: setUserSession
# Sets the user session key with information necessary to track
# a user's session. This method will do some basic validation.
#
# Parameters:
#    session - A session object
#    user - User object
#
# Returns:
#    A tuple of success and any error message. If everything is
#    successful then the message will be None
#
def setUserSession(session, user):
	if not user["id"]:
		return (False, "The provided user is invalid")

	session["user"] = user
	session.save()

	return (True, None)

#
# Function: userInSession
# This function checks the session dictionary for a key named
# "user". It will return true/false if the key is present
# in the session object.
#
# Parameters:
#    session - A session object
#
# Returns:
#    True/False if a user object is present in the session object
#
def userInSession(session):
	return "user" in session

