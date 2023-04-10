#!/bin/bash

cd /home/biff/Repositories/HAI-backend
source venv/bin/activate
gunicorn --certfile='/etc/letsencrypt/live/api.daveyonkers.com/cert.pem' --keyfile='/etc/letsencrypt/live/api.daveyonkers.com/privkey.pem' --bind 0.0.0.0:443 'server:create_app()'