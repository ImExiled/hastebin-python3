#!/bin/bash

source .venv/bin/activate

waitress-serve --port 5000 wsgi:app