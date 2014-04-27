#
# File: dthelper.py
# This package provides methods for working with dates and times.
# Many of the methods here offer simple wrappers for things like
# formatting a date for SQL or REST, retrieving parts of a date,
# and so on.
#
# Author:
#    Adam Presley
#
# Module:
#    services.datetimehelper
#
from dateutil import tz
from datetime import tzinfo
from datetime import datetime
from datetime import timedelta

import pytz
import calendar

###############################################################################
# Section: Module Variables
###############################################################################

# Variable: _utc
# Represents the UTC time zone
_utc = tz.gettz("UTC")

# Constant: REST_DATE_FORMAT
# A REST-style date format: *%Y-%m-%d*
REST_DATE_FORMAT = "%Y-%m-%d"

# Constant: REST_DATETIME_FORMAT
# A REST-style date and time format: *%Y-%m-%d %H:%M*
REST_DATETIME_FORMAT = "%Y-%m-%d %H:%M"

# Constant: US_DATE_FORMAT
# US-style date format: *%m/%d/%Y*
US_DATE_FORMAT = "%m/%d/%Y"

# Constant: US_DATETIME_FORMAT
# US-style date format: *%m/%d/%Y %I:%M %p*
US_DATE_FORMAT = "%m/%d/%Y %I:%M %p"

# CONSTANT: PY_TO_JS_FORMATS
# A dictionary of Python to JavaScript date formats
#    * "%m/%d/%Y": "MM/dd/yyyy"
#    * %d/%m/%Y": "dd/MM/yyyy
#    * %Y-%m-%d": "yyyy-MM-dd
PY_TO_JS_FORMATS = {
	"%m/%d/%Y": "MM/dd/yyyy",
	"%d/%m/%Y": "dd/MM/yyyy",
	"%Y-%m-%d": "yyyy-MM-dd"
}


###############################################################################
# Section: Functions
###############################################################################


#
# Function: addDays
# Adds a number of days to a specific date. Dates are parsed
# using the format *%Y-%m-%d* by default. This function
# returns a new date.
#
# Parameters:
#    date        - Initial date
#    numDays     - Number of days to add. Defaults to *1*
#    parseFormat - Format to parse the initial date with. Defaults to *%Y-%m-%d*
#
def addDays(date, numDays=1, parseFormat="%Y-%m-%d"):
	if not isDateType(date):
		date = datetime.strptime(date, parseFormat)

	return date + timedelta(days=numDays)

#
# Function: formatDate
# Parses an input date and returns it in a different format
# as specified by *outputFormat*.
#
# Parameters:
#    date         - Input date
#    outputFormat - The format of the returned date. Defaults to *%Y-%m-%d*
#    parseFormat  - Format to parse the initial date with. Defaults to *%Y-%m-%d*
#
def formatDate(date, outputFormat="%Y-%m-%d", parseFormat="%Y-%m-%d"):
	return _formatDateTime(date=date, outputFormat=outputFormat, parseFormat=parseFormat)

#
# Function: formatDateTime
# Parses an input date/time and returns it in a different format
# as specified by *outputFormat*.
#
# Parameters:
#    date         - Input date/time
#    outputFormat - The format of the returned date/time. Defaults to *%Y-%m-%d %H:%M*
#    parseFormat  - Format to parse the initial date with. Defaults to *%Y-%m-%d %H:%M*
#
def formatDateTime(date, outputFormat="%Y-%m-%d %H:%M", parseFormat="%Y-%m-%d %H:%M"):
	return _formatDateTime(date=date, outputFormat=outputFormat, parseFormat=parseFormat)

#
# Function: formatTime
# Parses an input date/time and returns the time only in the format
# specified by *outputFormat*.
#
# Parameters:
#    date         - Input date/time
#    outputFormat - The format of the returned time. Defaults to *%H:%M*
#    parseFormat  - Format to parse the inital date/time with. Defaults to *%Y-%m-%d %H:%M*
#
def formatTime(date, outputFormat="%H:%M", parseFormat="%H:%M"):
	return _formatDateTime(date=date, outputFormat=outputFormat, parseFormat=parseFormat)

#
# Function: fromTimestamp
# Returns a date from a timestamp.
#
# Parameters:
#    date - Input timestamp
#
def fromTimestamp(date):
	return datetime.fromtimestamp(date)

#
# Function: getMonth
# Returns the month part of a date.
#
# Parameters:
#    date        - Input date as a string or date object
#    parseFormat - Format to parse the initial date with. Defaults to *%Y-%m-%d*
#
def getMonth(date, parseFormat="%Y-%m-%d"):
	if not isDateType(date):
		date = datetime.strptime(date, parseFormat)

	return date.strftime("%m")

#
# Function: getTimezone
# Gets a timezone object from a string name.
#
# Parameters:
#    timezoneName - String of the timezone object to retrieve
#
def getTimezone(timezoneName):
	return tz.gettz(timezoneName)

#
# Function: getTimezoneArray
# Returns an array of common timezone strings.
#
def getTimezoneArray():
	return pytz.common_timezones

#
# Function: getYear
# Returns the year part of a date.
#
# Parameters:
#    date        - Input date as a string or date object
#    parseFormat - Format to parse the initial date with. Defaults to *%Y-%m-%d*
#
def getYear(date, parseFormat="%Y-%m-%d"):
	if not isDateType(date):
		date = datetime.strptime(date, parseFormat)

	return date.strftime("%Y")

#
# Function: isDateType
# Determines if a given date/time is a date object. This function will return
# True if the input *date* is a date object. Otherwise it returns False.
#
# Parameters:
#    date - Suspected date object
#
def isDateType(date):
	result = True

	try:
		date.today()
	except AttributeError as e:
		result = False

	return result

#
# Function: localNow
# Returns a date/time object local to a specified timezone from the current
# date/time in UTC.
#
# Parameters:
#    timezone - Timezone to convert to from UTC
#
def localNow(timezone):
	return utcToTimezone(utcNow, timezone)

#
# Function: utcNow
# Returns the current date/time in UTC.
#
def utcNow():
	return datetime.now(_utc)

#
# Function: parse
# Parses a date/time in a specified format. If the input date is already
# a date/time object it is simply returned. If not this method will
# attempt to parse it and return a new date/time object.
#
# Parameters:
#    date        - Input date as a string or date object
#    parseFormat - Expected format of the input date. Used to parse to a date/time object
#
def parse(date, parseFormat):
	if isDateType(date):
		return date
	else:
		return datetime.strptime(date, parseFormat)

#
# Function: parseDate
# Parses a date in the format of *%Y-%m-%d* and returns a date/time object.
#
# Parameters:
#    date        - Input date as a string or date object
#    parseFormat - Expected format of the input date. Used to parse to a date/time object. Defaults to *%Y-%m-%d*
#
def parseDate(date, parseFormat="%Y-%m-%d"):
	return parse(date=date, parseFormat=parseFormat)

#
# Function: parseDateTime
# Parses a date/time in the format of *%Y-%m-%d %H:%M* and returns a date/time object.
#
# Parameters:
#    date        - Input date as a string or date object
#    parseFormat - Expected format of the input date. Used to parse to a date/time object. Defaults to *%Y-%m-%d %H:%M*
#
def parseDateTime(date, parseFormat="%Y-%m-%d %H:%M"):
	return parse(date=date, parseFormat=parseFormat)

#
# Function: timezoneToUtc
# Takes an input date/time and a source timezone and returns a new date/time
# object in UTC time. For example, given 2:30AM US/Central the UTC time will be
# 07:30 UTC.
#
# Parameters:
#    sourceTimezone - A timezone object representing what to convert FROM
#    date           - Input date/time object
#
def timezoneToUtc(sourceTimezone, date, parseFormat="%Y-%m-%d %H:%M:%S"):
	sourceTZ = tz.gettz(sourceTimezone)
	date = parse(date=date, parseFormat=parseFormat)

	date = date.replace(tzinfo=sourceTZ)
	return date.astimezone(_utc)

#
# Function: toTimestamp
# This function will take a date/time object and return a timestamp (long).
#
# Parameters:
#    date - Input date (date/time object)
#
def toTimestamp(date):
	return calendar.timegm(date.utctimetuple())

#
# Function: utcToTimezone
# Takes an input date/time in the UTC timezone and returns a new date/time
# object local to the specified target timezone. For example, given 17:30 UTC
# and a target timezone of "US/Central" (which is -0600 in daylight savings time)
# this function will return a date/time object of 11:30 CST.
#
# Parameters:
#    targetTimezone - A timezone object representing the timezone to convert a date/time object to
#    date           - Input date/time object
#
def utcToTimezone(targetTimezone, date, parseFormat="%Y-%m-%d %H:%M:%S%z"):
	targetTZ = tz.gettz(targetTimezone)
	date = parse(date=date, parseFormat=parseFormat)

	date = date.replace(tzinfo=_utc)
	return date.astimezone(targetTZ)

#
# Function: validateDateRange
# Takes a start and end date, a maximum number of days for a valid range and
# attempts to validate them. If the delta between the start date and the end date
# do no exceed the maximum number of days then the original start and end dates
# are returned. If they do exceed the max days, today's date is return in UTC timezone.
#
# Parameters:
#    start       - Start date
#    end         - End date
#    maxDays     - Maximum number of days allowed between start and end
#    parseFormat - Format to parse dates with. Defaults to *%Y-%m-%d*
#
def validateDateRange(start, end, maxDays, parseFormat="%Y-%m-%d"):
	#
	# Basically if the range between start and end is greater than *maxDays*
	# days kick it back with today's date as default.
	#
	parsedStart = parse(date=start, parseFormat=parseFormat)
	parsedEnd = parse(date=end, parseFormat=parseFormat)

	delta = parsedEnd - parsedStart

	newStart = start
	newEnd = end

	if delta.days > maxDays:
		newStart = formatDateTime(date=utcNow())
		newEnd = formatDateTime(date=utcNow())

	return (newStart, newEnd)


def _formatDateTime(date, outputFormat, parseFormat):
	return date.strftime(outputFormat) if isDateType(date) else parse(date, parseFormat).strftime(outputFormat)
