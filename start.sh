#!/bin/sh
python gps_crawler.py &
gunicorn web:app -b 0.0.0.0:8000