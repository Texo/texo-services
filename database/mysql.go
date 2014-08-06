package database

import (
	"database/sql"
	"log"
	"os"
	"strconv"

	_ "github.com/go-sql-driver/mysql"
)

var Db *sql.DB

func ConnectMySQL(connectionInfo SqlConnection) error {
	/*
	 * Create the connection
	 */
	log.Println("Connecting to MySQL database...")

	db, err := sql.Open("mysql", connectionInfo.ToString())
	if err != nil {
		return err
	}

	temp := os.Getenv("max_connections")
	if temp == "" {
		temp = "151"
	}

	maxConnections, _ := strconv.Atoi(temp)

	db.SetMaxIdleConns(maxConnections)
	db.SetMaxOpenConns(maxConnections)

	Db = db
	return nil
}
