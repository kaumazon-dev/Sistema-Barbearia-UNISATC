import pytest
from marshmallow import ValidationError

from app.schemas.usuario_schema import (
    LoginSchema,
    UsuarioCadastroSchema,
    UsuarioFiltroSchema,
    UsuarioSchema,
)
from app.core.security import gerar_hash
from app.models.usuario import PAPEL_CLIENTE, Usuario

DADOS_VALIDOS = {
    "nome": "Maria",
    "email": "Maria@Exemplo.com",
    "senha": "senha-boa-123",
}


def test_email_e_normalizado_para_minusculo():
    dados = UsuarioCadastroSchema().load(DADOS_VALIDOS)

    assert dados["email"] == "maria@exemplo.com"


def test_papel_enviado_no_corpo_e_recusado():
    with pytest.raises(ValidationError) as erro:
        UsuarioCadastroSchema().load(dict(DADOS_VALIDOS, papel="admin"))

    assert "papel" in erro.value.messages


def test_senha_curta_e_recusada():
    with pytest.raises(ValidationError):
        UsuarioCadastroSchema().load(dict(DADOS_VALIDOS, senha="curta"))


def test_senha_acima_de_72_bytes_e_recusada():
    # 40 caracteres "ç" = 80 bytes em UTF-8.
    senha = "ç" * 40
    assert len(senha) < 72

    with pytest.raises(ValidationError):
        UsuarioCadastroSchema().load(dict(DADOS_VALIDOS, senha=senha))


def test_login_normaliza_email():
    dados = LoginSchema().load({"email": " JOAO@Exemplo.com ", "senha": "qualquer"})

    assert dados["email"] == "joao@exemplo.com"


def test_saida_nunca_inclui_senha_hash():
    usuario = Usuario(
        nome="João",
        email="joao@exemplo.com",
        senha_hash=gerar_hash("senha-boa-123"),
        papel=PAPEL_CLIENTE,
        ativo=True,
    )
    usuario.id = 1

    saida = UsuarioSchema().dump(usuario)

    assert "senha_hash" not in saida
    assert "senha" not in saida
    assert saida["email"] == "joao@exemplo.com"


def test_nome_so_com_espacos_e_recusado():
    with pytest.raises(ValidationError):
        UsuarioCadastroSchema().load(dict(DADOS_VALIDOS, nome="     "))


def test_nome_e_email_perdem_espacos_das_pontas():
    dados = UsuarioCadastroSchema().load(
        dict(DADOS_VALIDOS, nome="  Maria Silva  ")
    )

    assert dados["nome"] == "Maria Silva"


def test_filtro_recusa_papel_fora_do_enum():
    with pytest.raises(ValidationError):
        UsuarioFiltroSchema().load({"papel": "lixo"})


def test_filtro_trata_papel_vazio_como_ausente():
    assert UsuarioFiltroSchema().load({"papel": ""})["papel"] is None
    assert UsuarioFiltroSchema().load({})["papel"] is None


def test_filtro_ignora_parametro_desconhecido():
    assert UsuarioFiltroSchema().load({"pagina": "2"})["papel"] is None


def test_filtro_aceita_os_tres_papeis():
    for papel in ("admin", "barbeiro", "cliente"):
        assert UsuarioFiltroSchema().load({"papel": papel})["papel"] == papel
