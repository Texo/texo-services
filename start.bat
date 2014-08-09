@echo off

set TEXO_SERVER_ADDRESS=localhost
set TEXO_SERVER_PORT=8081

set TEXO_POSTS_PER_PAGE=10

set TEXO_SQL_ADDRESS=localhost
set TEXO_SQL_PORT=3306
set TEXO_SQL_DATABASE=texocms
set TEXO_SQL_USERNAME=root
set TEXO_SQL_PASSWORD=password

go run texo-services.go -serveraddress=%TEXO_SERVER_ADDRESS% -serverport=%TEXO_SERVER_PORT%