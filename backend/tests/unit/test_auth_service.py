"""Service de autenticacao, sem banco e sem subir o Flask.

Se algum destes testes precisar de create_app(), a Regra 2 ou a 5 foi quebrada.
"""

from unittest import mock

import pytest

from app.core.exceptions import Conflito, NaoAutorizada
from app.core.security import gerar_hash
from app.models.usuario import PAPEL_CLIENTE, Usuario
from app.services import auth_service
from app.services.auth_service import (
    MENSAGEM_CREDENCIAIS_INVALIDAS,
    AuthService,
)


class RepositorioFalso:
    """Duble do UsuarioRepository: guarda em lista, nao em banco."""

    def __init__(self, usuarios=None):
        self.usuarios = list(usuarios or [])
        self.proximo_id = len(self.usuarios) + 1
        self.desfeito = False

    def buscar_por_email(self, email):
        for usuario in self.usuarios:
            if usuario.email == email:
                return usuario
        return None

    def get_by_id(self, id):
        for usuario in self.usuarios:
            if usuario.id == id:
                return usuario
        return None

    def get_all(self):
        return list(self.usuarios)

    def listar_por_papel(self, papel):
        return [usuario for usuario in self.usuarios if usuario.papel == papel]

    def create(self, entidade):
        entidade.id = self.proximo_id
        self.proximo_id += 1
        self.usuarios.append(entidade)
        return entidade

    def desfazer(self):
        self.desfeito = True


def construir_usuario(email="joao@exemplo.com", senha="senha-boa-123", ativo=True):
    usuario = Usuario(
        nome="João",
        email=email,
        senha_hash=gerar_hash(senha),
        papel=PAPEL_CLIENTE,
        ativo=ativo,
    )
    usuario.id = 1
    return usuario


DADOS_CADASTRO = {
    "nome": "Maria",
    "email": "maria@exemplo.com",
    "senha": "senha-boa-123",
}


def test_cadastro_gera_hash_e_nunca_guarda_senha_pura():
    servico = AuthService(RepositorioFalso())

    usuario = servico.cadastrar(DADOS_CADASTRO)

    assert usuario.senha_hash != DADOS_CADASTRO["senha"]
    assert usuario.senha_hash.startswith("$2b$")


def test_cadastro_sempre_cria_com_papel_cliente():
    servico = AuthService(RepositorioFalso())

    dados = dict(DADOS_CADASTRO, papel="admin")
    usuario = servico.cadastrar(dados)

    assert usuario.papel == PAPEL_CLIENTE


def test_cadastro_recusa_email_duplicado():
    existente = construir_usuario(email=DADOS_CADASTRO["email"])
    servico = AuthService(RepositorioFalso([existente]))

    with pytest.raises(Conflito):
        servico.cadastrar(DADOS_CADASTRO)


def test_login_valido_devolve_o_usuario():
    usuario = construir_usuario()
    servico = AuthService(RepositorioFalso([usuario]))

    assert servico.autenticar(usuario.email, "senha-boa-123") is usuario


def test_login_com_senha_errada_recusa():
    usuario = construir_usuario()
    servico = AuthService(RepositorioFalso([usuario]))

    with pytest.raises(NaoAutorizada):
        servico.autenticar(usuario.email, "senha-errada-123")


def test_login_de_usuario_desativado_recusa():
    usuario = construir_usuario(ativo=False)
    servico = AuthService(RepositorioFalso([usuario]))

    with pytest.raises(NaoAutorizada):
        servico.autenticar(usuario.email, "senha-boa-123")


def test_login_de_email_inexistente_gasta_tempo_de_verificacao():
    """O tempo de resposta nao pode revelar se o e-mail existe."""
    servico = AuthService(RepositorioFalso())
    chamadas = []

    with mock.patch.object(
        auth_service, "gastar_tempo_de_verificacao", lambda: chamadas.append(1)
    ):
        with pytest.raises(NaoAutorizada):
            servico.autenticar("nao-existe@exemplo.com", "senha-boa-123")

    assert chamadas == [1]


def test_login_de_usuario_desativado_gasta_tempo_de_verificacao():
    servico = AuthService(RepositorioFalso([construir_usuario(ativo=False)]))
    chamadas = []

    with mock.patch.object(
        auth_service, "gastar_tempo_de_verificacao", lambda: chamadas.append(1)
    ):
        with pytest.raises(NaoAutorizada):
            servico.autenticar("joao@exemplo.com", "senha-boa-123")

    assert chamadas == [1]


def test_email_inexistente_e_senha_errada_dao_a_mesma_mensagem():
    usuario = construir_usuario()
    servico = AuthService(RepositorioFalso([usuario]))

    with pytest.raises(NaoAutorizada) as erro_senha:
        servico.autenticar(usuario.email, "senha-errada-123")

    with pytest.raises(NaoAutorizada) as erro_email:
        servico.autenticar("nao-existe@exemplo.com", "senha-boa-123")

    assert erro_senha.value.mensagem == erro_email.value.mensagem
    assert erro_senha.value.mensagem == MENSAGEM_CREDENCIAIS_INVALIDAS
