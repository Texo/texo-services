package controllers

import (
	"fmt"
	"log"
	"net/http"
	"strconv"

	"github.com/gorilla/mux"
	"github.com/texo/texo-services/services/httpservice"
	"github.com/texo/texo-services/services/postservice"
)

/*
Retrieves a single tag by ID.

URL: /v1/tag/{id}
*/
func GetTag_v1(writer http.ResponseWriter, request *http.Request) {
	vars := mux.Vars(request)

	id, _ := strconv.Atoi(vars["id"])

	tag, err := postservice.GetTag(id)
	if err != nil {
		log.Println("ERROR - ", err.Error())
		httpservice.Error(writer, fmt.Sprintf("There was an error getting the tag with ID %d", id))
		return
	}

	if tag.Id == 0 {
		httpservice.NotFound(writer, fmt.Sprintf("Could not find tag %d", id))
		return
	}

	httpservice.WriteJson(writer, tag, 200)
}

/*
Retrieves all tags used in blog posts. Tags are ordered by most frequently used first.

URL: /v1/tags
*/
func GetTags_v1(writer http.ResponseWriter, request *http.Request) {
	tags, err := postservice.GetTags()
	if err != nil {
		log.Println("ERROR - ", err.Error())
		httpservice.Error(writer, "There was an error getting tags")
		return
	}

	httpservice.WriteJson(writer, tags, 200)
}
