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

	return router
}