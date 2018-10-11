#!/bin/sh
while true; do inotifywait -e CLOSE_WRITE *.py; clear; pytest quest_parse.py $@; done
