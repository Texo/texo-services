package environment

import (
	"fmt"
	"os"
	"strconv"

	"github.com/texo/texo-services/database"
)

/*
Gets the number of posts to display on a page from
the environment configuration.
*/
func GetPostsPerPageSetting() int {
	postsPerPageString := os.Getenv(ENV_POSTS_PER_PAGE)
	if postsPerPageString == "" {
		postsPerPageString = "10"
	}

	postsPerPage, _ := strconv.Atoi(postsPerPageString)
	return postsPerPage
}

/*
Reads environment variables to get SQL server connection
information and returns a SqlConnection object. The following
constants represent the environment variables that are read:

   * ENV_SQL_ADDRESS
   * ENV_SQL_PORT
   * ENV_SQL_DATABASE
   * ENV_SQL_USERNAME
   * ENV_SQL_PASSWORD
*/
func GetSqlConnectionInformation() (database.SqlConnection, error) {
	var err error
	var connectionInfo database.SqlConnection

	address := os.Getenv(ENV_SQL_ADDRESS)
	if address == "" {
		return connectionInfo, fmt.Errorf("Invalid environment variable %s", ENV_SQL_ADDRESS)
	}

	portString := os.Getenv(ENV_SQL_PORT)
	if portString == "" {
		return connectionInfo, fmt.Errorf("Invalid environment variable %s", ENV_SQL_PORT)
	}

	port, err := strconv.Atoi(portString)
	if err != nil {
		return connectionInfo, fmt.Errorf("Invalid SQL port: %s", err.Error())
	}

	databaseName := os.Getenv(ENV_SQL_DATABASE)
	if databaseName == "" {
		return connectionInfo, fmt.Errorf("Invalid environment variable %s", ENV_SQL_DATABASE)
	}

	userName := os.Getenv(ENV_SQL_USERNAME)
	if userName == "" {
		return connectionInfo, fmt.Errorf("Invalid environment variable %s", ENV_SQL_USERNAME)
	}

	password := os.Getenv(ENV_SQL_PASSWORD)
	if password == "" {
		return connectionInfo, fmt.Errorf("Invalid environment variable %s", ENV_SQL_PASSWORD)
	}

	connectionInfo = database.SqlConnection{
		Address:  address,
		Port:     port,
		Database: databaseName,
		UserName: userName,
		Password: password,
	}

	return connectionInfo, nil
}