#!/bin/bash

export PYTHONPATH="./:./app"
export PYTHONDONTWRITEBYTECODE="True"
export TEXO_SETTINGS_DEBUG="True"

source ./virtualenv/bin/activate
python -B ./app/www/texoservices.py
deactivate