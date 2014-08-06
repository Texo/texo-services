package httpservice

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
//	"strconv"
)

type BasicResponseMessage struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

func BadRequest(writer http.ResponseWriter, message string) {
	result := BasicResponseMessage{
		Success: false,
		Message: message,
	}

	WriteJson(writer, result, 400)
}

func Error(writer http.ResponseWriter, message string) {
	result := BasicResponseMessage{
		Success: false,
		Message: message,
	}

	WriteJson(writer, result, 500)
}

func ParseJsonBody(req *http.Request, receiver interface{}) (error) {
	var err error

	body, _ := ioutil.ReadAll(req.Body)
	err = json.Unmarshal(body, receiver)
	return err
}

func Success(writer http.ResponseWriter, message string) {
	result := BasicResponseMessage{
		Success: true,
		Message: message,
	}

	WriteJson(writer, result, 200)
}

func WriteJson(writer http.ResponseWriter, object interface{}, code int) {
	json, _ := json.Marshal(object)
	content := string(json)
	size := len(json)

	writer.Header().Set("Content-Type", "application/json")
	//writer.Header().Add("Content-Length", strconv.Itoa(size))
	writer.WriteHeader(code)
	fmt.Fprintf(writer, content)
}
