from sqlalchemy.exc import IntegrityError

from app.core.exceptions import Conflito, NaoEncontrado
from app.models.usuario import PAPEL_CLIENTE
from app.services.auth_service import AuthService


class ClienteService:
    """Cliente nao tem tabela propria: e um usuario com papel = cliente (DER).

    Cliente nunca e apagado de fato, so desativado (RF06): o historico de
    agendamentos e o dashboard dependem dele.
    """

    def __init__(self, repositorio):
        self.repositorio = repositorio

    def listar(self, busca=None, ativo=None, pagina=1, por_pagina=20):
        return self.repositorio.buscar_por_papel(
            PAPEL_CLIENTE, busca=busca, ativo=ativo, pagina=pagina, por_pagina=por_pagina
        )

    def buscar(self, cliente_id):
        usuario = self.repositorio.get_by_id(cliente_id)
        # Admin e barbeiro tambem estao na tabela usuario; por esta rota eles
        # simplesmente nao existem.
        if usuario is None or usuario.papel != PAPEL_CLIENTE:
            raise NaoEncontrado(f"Cliente {cliente_id} não existe.")
        return usuario

    def cadastrar(self, dados):
        # Mesma regra do cadastro publico: papel fixo em cliente, senha em hash
        # e e-mail unico. Reaproveita em vez de duplicar.
        return AuthService(self.repositorio).cadastrar(dados)

    def atualizar(self, cliente_id, dados):
        cliente = self.buscar(cliente_id)

        email = dados.get("email")
        if email is not None and email != cliente.email:
            if self.repositorio.buscar_por_email(email) is not None:
                raise Conflito(f"Já existe um usuário cadastrado com o e-mail {email}.")

        for campo in ("nome", "email", "telefone", "ativo"):
            if campo in dados:
                setattr(cliente, campo, dados[campo])

        try:
            return self.repositorio.update(cliente)
        except IntegrityError:
            self.repositorio.desfazer()
            raise Conflito(f"Já existe um usuário cadastrado com o e-mail {email}.")

    def desativar(self, cliente_id):
        cliente = self.buscar(cliente_id)
        cliente.ativo = False
        return self.repositorio.update(cliente)
