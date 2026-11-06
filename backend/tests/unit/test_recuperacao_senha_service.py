"""Esqueci minha senha, sem banco e sem Flask."""

import time

import pytest

from app.core.exceptions import RegraDeNegocioViolada
from app.core.security import TokenRedefinicaoSenha, gerar_hash, verificar_senha
from app.models.usuario import PAPEL_CLIENTE, Usuario
from app.services.recuperacao_senha_service import (
    MENSAGEM_LINK_INVALIDO,
    RecuperacaoSenhaService,
)


class RepositorioFalso:
    def __init__(self, usuarios):
        self.usuarios = list(usuarios)
        self.atualizados = 0

    def buscar_por_email(self, email):
        return next((u for u in self.usuarios if u.email == email), None)

    def get_by_id(self, id):
        return next((u for u in self.usuarios if u.id == id), None)

    def update(self, entidade):
        self.atualizados += 1
        return entidade


class EnviadorFalso:
    def __init__(self):
        self.enviados = []

    def enviar(self, para, assunto, corpo):
        self.enviados.append({"para": para, "assunto": assunto, "corpo": corpo})


def usuario(id=1, email="ana@exemplo.com", ativo=True, senha="senha-antiga-1"):
    return Usuario(
        id=id,
        nome="Ana",
        email=email,
        senha_hash=gerar_hash(senha),
        papel=PAPEL_CLIENTE,
        ativo=ativo,
    )


def montar(*usuarios, validade=1800):
    repositorio = RepositorioFalso(usuarios)
    enviador = EnviadorFalso()
    tokens = TokenRedefinicaoSenha("segredo-de-teste", validade)
    servico = RecuperacaoSenhaService(
        repositorio, tokens, enviador, "http://front.local/"
    )
    return servico, repositorio, enviador, tokens


def token_do_email(enviado):
    return enviado["corpo"].split("?redefinir=")[1].split()[0]


def test_solicitar_envia_link_para_o_email_da_conta():
    servico, _, enviador, _ = montar(usuario())

    servico.solicitar("ana@exemplo.com")

    assert len(enviador.enviados) == 1
    assert enviador.enviados[0]["para"] == "ana@exemplo.com"
    assert "http://front.local/?redefinir=" in enviador.enviados[0]["corpo"]


@pytest.mark.parametrize("email, ativo", [("ninguem@exemplo.com", True), ("ana@exemplo.com", False)])
def test_solicitar_email_inexistente_ou_desativado_nao_envia_e_nao_erra(email, ativo):
    servico, _, enviador, _ = montar(usuario(ativo=ativo))

    servico.solicitar(email)  # nao lanca: a rota responde igual nos dois casos

    assert enviador.enviados == []


def test_redefinir_troca_a_senha():
    ana = usuario()
    servico, repositorio, enviador, _ = montar(ana)
    servico.solicitar(ana.email)

    servico.redefinir(token_do_email(enviador.enviados[0]), "senha-nova-123")

    assert verificar_senha("senha-nova-123", ana.senha_hash)
    assert not verificar_senha("senha-antiga-1", ana.senha_hash)
    assert repositorio.atualizados == 1


def test_link_vale_uma_vez_so():
    ana = usuario()
    servico, _, enviador, _ = montar(ana)
    servico.solicitar(ana.email)
    token = token_do_email(enviador.enviados[0])
    servico.redefinir(token, "senha-nova-123")

    with pytest.raises(RegraDeNegocioViolada) as erro:
        servico.redefinir(token, "outra-senha-456")
    assert erro.value.mensagem == MENSAGEM_LINK_INVALIDO


def test_token_adulterado_e_recusado():
    servico, _, enviador, _ = montar(usuario())
    servico.solicitar("ana@exemplo.com")
    token = token_do_email(enviador.enviados[0])

    with pytest.raises(RegraDeNegocioViolada):
        servico.redefinir(token[:-2] + "xx", "senha-nova-123")


def test_token_de_outra_chave_e_recusado():
    ana = usuario()
    servico, _, _, _ = montar(ana)
    token_forjado = TokenRedefinicaoSenha("chave-do-atacante", 1800).gerar(ana)

    with pytest.raises(RegraDeNegocioViolada):
        servico.redefinir(token_forjado, "senha-nova-123")


def test_token_expirado_e_recusado(monkeypatch):
    ana = usuario()
    servico, _, _, tokens = montar(ana, validade=60)
    token = tokens.gerar(ana)

    agora = time.time()
    monkeypatch.setattr(time, "time", lambda: agora + 61)

    with pytest.raises(RegraDeNegocioViolada):
        servico.redefinir(token, "senha-nova-123")


def test_conta_desativada_depois_do_pedido_nao_redefine():
    ana = usuario()
    servico, _, _, tokens = montar(ana)
    token = tokens.gerar(ana)
    ana.ativo = False

    with pytest.raises(RegraDeNegocioViolada):
        servico.redefinir(token, "senha-nova-123")
