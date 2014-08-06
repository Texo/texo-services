package controllers

import (
	"log"
	"net/http"
	"strconv"
"encoding/json"

	"github.com/gorilla/mux"
	"github.com/texo/texo-services/environment"
	"github.com/texo/texo-services/services/httpservice"
	"github.com/texo/texo-services/services/postservice"
)

func GetPageOfPublicPosts_v1(writer http.ResponseWriter, request *http.Request) {
	vars := mux.Vars(request)
	pageNumberString := vars["pageNumber"]
	pageNumber, _ := strconv.Atoi(pageNumberString)

	posts, err := postservice.GetPublishedPosts(pageNumber, environment.GetPostsPerPageSetting())
	if err != nil {
		log.Println("ERROR - ", err.Error())
		httpservice.Error(writer, "There was an error getting published posts")
		return
	}

	json, _ := json.Marshal(posts)
	content := string(json)
	log.Println(content)

	httpservice.WriteJson(writer, posts, 200)
}
