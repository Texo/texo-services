package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"runtime"
	"time"

	"github.com/adampresley/sigint"
	"github.com/justinas/alice"

	"github.com/texo/texo-services/bootstrapper"
	"github.com/texo/texo-services/environment"
	"github.com/texo/texo-services/database"
)

var serverPort = flag.Int("serverport", 8081, "Port for web server")
var serverAddress = flag.String("serveraddress", "localhost", "Address for web server")

func main() {
	var err error

	flag.Parse()
	runtime.GOMAXPROCS(runtime.NumCPU())

	/*
	 * Handle SIGINT (CTRL+C)
	 */
	sigint.ListenForSIGINT(func() {
		log.Println("Shutting down...")
		os.Exit(0)
	})

	/*
	 * Setup database
	 */
	connectionInfo, err := environment.GetSqlConnectionInformation()
	if err != nil {
		log.Fatal(err)
	}

	err = database.ConnectMySQL(connectionInfo)
	if err != nil {
		log.Fatal(err)
	}

	/*
	 * Setup routing and middleware
	 */
	router := bootstrapper.SetupWebRouter()
	middleware := alice.New(auth, logger).Then(router)

	/*
	 * Start web server
	 */
	log.Printf("Texo Services setup on %s:%d\n\n", *serverAddress, *serverPort)
	http.ListenAndServe(fmt.Sprintf("%s:%d", *serverAddress, *serverPort), middleware)
}

func auth(h http.Handler) http.Handler {
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		log.Println("Authorizing...")
		h.ServeHTTP(writer, request)
	})
}

func logger(h http.Handler) http.Handler {
	return http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		startTime := time.Now()
		h.ServeHTTP(writer, request)
		log.Printf("%s - %s (%v)\n", request.Method, request.URL.Path, time.Since(startTime))
	})
}
