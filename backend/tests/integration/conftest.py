"""Testes de rota + banco real, usando TestConfig (DATABASE_URL_TEST).

O banco de teste precisa existir antes. Com o compose de pe:
    docker compose exec db createdb -U barbearia barbearia_test
"""

import os

import pytest

os.environ["APP_ENV"] = "test"

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.usuario import (  # noqa: E402
    PAPEL_ADMIN,
    PAPEL_BARBEIRO,
    PAPEL_CLIENTE,
)
from tests.integration.fabricas import cabecalho_de, criar_usuario  # noqa: E402


@pytest.fixture(scope="session")
def app():
    app = create_app()
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        pytest.skip("DATABASE_URL_TEST nao configurada.")
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def banco_limpo(app):
    yield
    db.session.rollback()
    # TRUNCATE e nao DELETE: movimentacao_estoque tem trigger que recusa
    # DELETE (historico imutavel). TRUNCATE nao dispara trigger de linha.
    tabelas = ", ".join(f'"{t.name}"' for t in db.metadata.sorted_tables)
    db.session.execute(db.text(f"TRUNCATE TABLE {tabelas}"))
    db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin():
    return cabecalho_de(criar_usuario(PAPEL_ADMIN))


@pytest.fixture
def barbeiro():
    return cabecalho_de(criar_usuario(PAPEL_BARBEIRO))


@pytest.fixture
def cliente_logado():
    return cabecalho_de(criar_usuario(PAPEL_CLIENTE))
