#!/bin/sh
set -e

# TODO F1: descomentar quando Flask-Migrate estiver instalado e migrations/ existir.
# flask --app app db upgrade

exec "$@"
