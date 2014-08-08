package httpservice

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
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

func NotFound(writer http.ResponseWriter, message string) {
	result := BasicResponseMessage{
		Success: false,
		Message: message,
	}

	WriteJson(writer, result, 404)
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
	jsonBytes, _ := json.Marshal(object)
	content := strings.Replace(string(jsonBytes), "%", "%%", -1)
	//size := len(json)

	writer.Header().Set("Content-Type", "application/json; charset=UTF-8")
	//writer.Header().Add("Content-Length", strconv.Itoa(size))
	writer.WriteHeader(code)
	fmt.Fprintf(writer, content)
}
