#!/bin/sh
export FLASK_APP=./rest_neem_interface/RESTClient.py
export FLASK_RUN_PORT=8000
export FLASK_ENV=development
pipenv run flask run -h 0.0.0.0
