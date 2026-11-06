"""Service de cliente, sem banco e sem subir o Flask."""

import pytest

from app.core.exceptions import Conflito, NaoEncontrado
from app.models.usuario import PAPEL_BARBEIRO, PAPEL_CLIENTE, Usuario
from app.services.cliente_service import ClienteService


class RepositorioFalso:
    """Duble do UsuarioRepository: guarda em lista, nao em banco."""

    def __init__(self, usuarios=None):
        self.usuarios = list(usuarios or [])
        self.proximo_id = len(self.usuarios) + 1
        self.chamadas_busca = []

    def buscar_por_email(self, email):
        return next((u for u in self.usuarios if u.email == email), None)

    def get_by_id(self, id):
        return next((u for u in self.usuarios if u.id == id), None)

    def buscar_por_papel(self, papel, **filtros):
        self.chamadas_busca.append((papel, filtros))
        return [], 0

    def create(self, entidade):
        entidade.id = self.proximo_id
        self.proximo_id += 1
        self.usuarios.append(entidade)
        return entidade

    def update(self, entidade):
        return entidade

    def desfazer(self):
        pass


def construir_usuario(id, email, papel=PAPEL_CLIENTE, ativo=True):
    usuario = Usuario(
        nome="Fulano", email=email, senha_hash="x", papel=papel, ativo=ativo
    )
    usuario.id = id
    return usuario


def test_listar_filtra_sempre_pelo_papel_cliente():
    repositorio = RepositorioFalso()

    ClienteService(repositorio).listar(busca="joao", ativo=True, pagina=2, por_pagina=10)

    papel, filtros = repositorio.chamadas_busca[0]
    assert papel == PAPEL_CLIENTE
    assert filtros == {"busca": "joao", "ativo": True, "pagina": 2, "por_pagina": 10}


def test_buscar_cliente_inexistente_recusa():
    with pytest.raises(NaoEncontrado):
        ClienteService(RepositorioFalso()).buscar(99)


def test_buscar_usuario_que_nao_e_cliente_recusa():
    barbeiro = construir_usuario(1, "barbeiro@x.com", papel=PAPEL_BARBEIRO)

    with pytest.raises(NaoEncontrado):
        ClienteService(RepositorioFalso([barbeiro])).buscar(1)


def test_cadastrar_cria_com_papel_cliente_e_hash():
    servico = ClienteService(RepositorioFalso())

    cliente = servico.cadastrar(
        {"nome": "Maria", "email": "maria@x.com", "senha": "senha-boa-123", "papel": "admin"}
    )

    assert cliente.papel == PAPEL_CLIENTE
    assert cliente.senha_hash.startswith("$2b$")


def test_atualizar_recusa_email_de_outro_usuario():
    cliente = construir_usuario(1, "cliente@x.com")
    outro = construir_usuario(2, "outro@x.com", papel=PAPEL_BARBEIRO)
    servico = ClienteService(RepositorioFalso([cliente, outro]))

    with pytest.raises(Conflito):
        servico.atualizar(1, {"email": "outro@x.com"})


def test_atualizar_mantendo_o_proprio_email_e_permitido():
    cliente = construir_usuario(1, "cliente@x.com")
    servico = ClienteService(RepositorioFalso([cliente]))

    atualizado = servico.atualizar(1, {"email": "cliente@x.com", "nome": "Novo Nome"})

    assert atualizado.nome == "Novo Nome"


def test_atualizar_altera_so_os_campos_enviados():
    cliente = construir_usuario(1, "cliente@x.com")
    cliente.telefone = "4899999"
    servico = ClienteService(RepositorioFalso([cliente]))

    servico.atualizar(1, {"nome": "Outro"})

    assert cliente.telefone == "4899999"
    assert cliente.email == "cliente@x.com"


def test_desativar_nao_apaga_so_marca_inativo():
    cliente = construir_usuario(1, "cliente@x.com")
    repositorio = RepositorioFalso([cliente])

    ClienteService(repositorio).desativar(1)

    assert cliente.ativo is False
    assert cliente in repositorio.usuarios
