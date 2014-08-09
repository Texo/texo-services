#!/bin/bash

export TEXO_SERVER_ADDRESS=localhost
export TEXO_SERVER_PORT=8081

export TEXO_POSTS_PER_PAGE=10

export TEXO_SQL_ADDRESS=localhost
export TEXO_SQL_PORT=3306
export TEXO_SQL_DATABASE=texocms
export TEXO_SQL_USERNAME=root
export TEXO_SQL_PASSWORD=password

go run ./texo-services.go -serveraddress=$TEXO_SERVER_ADDRESS -serverport=$TEXO_SERVER_PORT
