package bootstrapper

import (
	"github.com/gorilla/mux"

	"github.com/texo/texo-services/controllers"
)

/*
Sets up an HTTP router. This router maps URL resources to
controller methods.
*/
func SetupWebRouter() *mux.Router {
	router := mux.NewRouter()

	router.HandleFunc("/v1/test", controllers.Test_v1).Methods("GET", "OPTIONS")

	/*
	 * Posts
	 */
	router.HandleFunc("/v1/posts/{pageNumber:[0-9]+}", controllers.GetPageOfPublicPosts_v1).Methods("GET", "OPTIONS")
	router.HandleFunc("/v1/posts/{pageNumber:[0-9]+}/tag/{tag}", controllers.GetPageOfPublicPostsByTag_v1).Methods("GET", "OPTIONS")
	router.HandleFunc("/v1/posts/{pageNumber:[0-9]+}/search/{term}", controllers.GetPageOfPublicPostsByTerm_v1).Methods("GET", "OPTIONS")
	router.HandleFunc("/v1/post/{year:[0-9]+}/{month:[0-9]+}/{slug}", controllers.GetPost_v1).Methods("GET", "OPTIONS")

	/*
	 * Tags
	 */
	router.HandleFunc("/v1/tags", controllers.GetTags_v1).Methods("GET", "OPTIONS")
	router.HandleFunc("/v1/tag/{id:[0-9]+}", controllers.GetTag_v1).Methods("GET", "OPTIONS")

	return router
}