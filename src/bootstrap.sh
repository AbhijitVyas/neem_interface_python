#!/bin/sh
export FLASK_APP=./rest_neem_interface/RESTClient.py
pipenv run flask --debug run -h 0.0.0.0