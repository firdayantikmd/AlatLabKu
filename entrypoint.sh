#!/bin/bash

# Check the command provided
case "$1" in
  flask)
    shift
    # Use the FLASK_APP environment variable
    FLASK_APP=${FLASK_APP:-run.py} exec flask "$@"
    ;;
  *)
    exec "$@"
    ;;
esac
