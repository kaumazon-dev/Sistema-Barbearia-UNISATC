#!/bin/sh
set -e


flask --app app db upgrade

# Dados de exemplo para a demo (Render: RODAR_SEED=1). O seed e idempotente:
# se o banco ja foi populado, ele nao faz nada.
if [ "$RODAR_SEED" = "1" ]; then
    python seed.py
fi

exec "$@"
