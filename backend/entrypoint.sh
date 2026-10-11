#!/bin/sh
set -e


flask --app app db upgrade

exec "$@"
