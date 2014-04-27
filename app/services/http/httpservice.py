#
# File: httpservice.py
# This module provides helper methods used to build HTTP responses.
#
# Author:
#    Adam Presley
#

#
# Function: badRequest
# This function sets a status of 400 and returns a JSON response
# with *success* set to False and a message. This is useful
# for situations when perhaps a request does not contain all the
# expected arguments, or perhaps some data in those arguments
# is invalid.
#
# Parameters:
#    message - Message about error
#
# Returns:
#    Sets status to 400 and returns a JSON structure.
#
#    > {
#    >    success: false,
#    >    message: "Bad Request"
#    > }
#
def badRequest(response, message="Bad Request"):
	response.status = 400
	return _buildMessage(success=False, message=message)

#
# Function: error
# This function sets a status of 500 and returns a JSON response
# with *success* set to False and a message. This is useful
# for situations when things have just gone horribly wrong.
#
# Parameters:
#    response - HTTP response object
#    message - Message about error
#    asString - True/False to return simple string instead of JSON object
#
# Returns:
#    Sets status to 500 and returns a JSON structure.
#
#    > {
#    >    success: false,
#    >    message: "A server error occurred"
#    > }
#
def error(response, message, asString=False):
	response.status = 500
	return _buildMessage(success=False, message=message, asString=asString)

#
# Function: notAuthorized
# This function sets a status of 401 and returns a JSON response
# with *success* set to False and a message. This is useful
# for situations when a request has been made that a user
# isn't authorized to use, or perhaps the request isn't
# even authorized.
#
# Returns:
#    Sets status to 401 and returns a JSON structure.
#
#    > {
#    >    success: false,
#    >    message: "Unauthorized"
#    > }
#
def notAuthorized(response):
	response.status = 401
	return _buildMessage(success=False, message="Unauthorized")

#
# Function: notFound
# This function sets a status of 404 and returns a JSON response
# with *success* set to False and a message. This is useful
# for situations when a requested resource doesn't exist.
#
# Parameters:
#    message - Message about error
#
# Returns:
#    Sets status to 404 and returns a JSON structure.
#
#    > {
#    >    success: false,
#    >    message: "Not Found"
#    > }
#
def notFound(response, message="Not Found"):
	response.status = 404
	return _buildMessage(success=False, message=message)


def _buildMessage(success, message, asString=False):
	if asString:
		result = message
	else:
		result = {
			"success": success,
			"message": message
		}

	return result