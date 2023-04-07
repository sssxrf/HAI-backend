#!/bin/bash

cd /home/biff/Repositories/HAI-backend
source venv/bin/activate
waitress-serve --port=80 --call server:create_app