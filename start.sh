#!/bin/bash

export TEXO_SQL_ADDRESS=localhost
export TEXO_SQL_PORT=3306
export TEXO_SQL_DATABASE=texocms
export TEXO_SQL_USERNAME=root
export TEXO_SQL_PASSWORD=password

go run ./texo-services.go
