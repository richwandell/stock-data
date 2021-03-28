#!/usr/bin/env bash
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=run.py

npm install
grunt copy webpack:vis
flask run --host=0.0.0.0