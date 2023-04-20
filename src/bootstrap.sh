#!/bin/sh
export FLASK_APP=./rest_neem_interface/RESTClient.py
export FLASK_RUN_PORT=8000
pipenv run flask --debug run -h 0.0.0.0