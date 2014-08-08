package controllers

import (
	"fmt"
	"log"
	"net/http"
	"strconv"

	"github.com/gorilla/mux"
	"github.com/texo/texo-services/environment"
	"github.com/texo/texo-services/services/httpservice"
	"github.com/texo/texo-services/services/postservice"
)

/*
Retrieves a single page of blog posts. Only published posts are retrieved.
This method is bested used when displaying published posts, such as on
a blog home page.

URL: /v1/posts/{pageNumber}
*/
func GetPageOfPublicPosts_v1(writer http.ResponseWriter, request *http.Request) {
	vars := mux.Vars(request)

	pageNumber, _ := strconv.Atoi(vars["pageNumber"])

	posts, err := postservice.GetPublishedPosts(pageNumber, environment.GetPostsPerPageSetting())
	if err != nil {
		log.Println("ERROR - ", err.Error())
		httpservice.Error(writer, "There was an error getting published posts")
		return
	}

	httpservice.WriteJson(writer, posts, 200)
}

/*
Retrieves a single page of blog posts filtered by tag. Only published
posts are retrieved. This method is bested used when displaying published
posts, such as on a blog home page.

URL: /v1/posts/{pageNumber}/tag/{tag}
*/
func GetPageOfPublicPostsByTag_v1(writer http.ResponseWriter, request *http.Request) {
	vars := mux.Vars(request)

	pageNumber, _ := strconv.Atoi(vars["pageNumber"])
	tag := vars["tag"]

	posts, err := postservice.GetPublishedPostsByTag(pageNumber, environment.GetPostsPerPageSetting(), tag)
	if err != nil {
		log.Println("ERROR - ", err.Error())
		httpservice.Error(writer, "There was an error getting published posts by tag")
		return
	}

	httpservice.WriteJson(writer, posts, 200)
}

/*
Retrieves a single page of blog posts filtered by a search term. Only published
posts are retrieved. This method is bested used when displaying published
posts, such as on a blog home page.

URL: /v1/posts/{pageNumber}/search/{term}
*/
func GetPageOfPublicPostsByTerm_v1(writer http.ResponseWriter, request *http.Request) {
	vars := mux.Vars(request)

	pageNumber, _ := strconv.Atoi(vars["pageNumber"])
	term := vars["term"]

	posts, err := postservice.GetPublishedPostsByTerm(pageNumber, environment.GetPostsPerPageSetting(), term)
	if err != nil {
		log.Println("ERROR - ", err.Error())
		httpservice.Error(writer, "There was an error getting published posts by search term")
		return
	}

	httpservice.WriteJson(writer, posts, 200)
}

/*
Retrieves a single post entry by year, month, and slug.

URL: /v1/post/{year}/{month}/{slug}
*/
func GetPost_v1(writer http.ResponseWriter, request *http.Request) {
	vars := mux.Vars(request)

	year, _ := strconv.Atoi(vars["year"])
	month, _ := strconv.Atoi(vars["month"])
	slug := vars["slug"]

	post, err := postservice.GetPost(year, month, slug)
	if err != nil {
		log.Println("ERROR - ", err.Error())
		httpservice.Error(writer, "There was a problem getting your post")
		return
	}

	/*
	 * If the post comes back empty return a 404
	 */
	if post.Id == 0 {
		httpservice.NotFound(writer, fmt.Sprintf("Post for %s could not be found", postservice.CreatePermalink(year, month, slug)))
		return
	}

	httpservice.WriteJson(writer, post, 200)
}