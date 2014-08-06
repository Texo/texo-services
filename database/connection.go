package database

import (
	"fmt"
)

/*
SqlConnection contains data necessary to establish a connection
to a SQL server.
*/
type SqlConnection struct {
	Address  string
	Port     int
	Database string
	UserName string
	Password string
}

func (this *SqlConnection) ToString() string {
	return fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?autocommit=true", this.UserName, this.Password, this.Address, this.Port, this.Database)
}