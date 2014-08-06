package controllers

import (
	"fmt"
	"net/http"

//	"github.com/texo/texo-services/database"
	"github.com/texo/texo-services/services/httpservice"
)

func Test_v1(writer http.ResponseWriter, request *http.Request) {
	//var err error

	if request.Method == "OPTIONS" {
		fmt.Fprintf(writer, "")
		return
	}

	httpservice.Success(writer, "Person created successfully!")
}

