import pytest

from app.extensions import db
from app.models.usuario import PAPEL_BARBEIRO, PAPEL_CLIENTE, Usuario
from tests.integration.fabricas import criar_usuario

URL = "/api/v1/clientes"
NOVO_CLIENTE = {
    "nome": "Maria Souza",
    "email": "Maria@Exemplo.com",
    "senha": "senha-boa-123",
    "telefone": "48999990000",
}


def test_admin_cadastra_cliente(client, admin):
    resposta = client.post(URL, json=NOVO_CLIENTE, headers=admin)

    assert resposta.status_code == 201
    corpo = resposta.get_json()
    assert corpo["papel"] == PAPEL_CLIENTE
    assert corpo["email"] == "maria@exemplo.com"
    assert "senha" not in corpo and "senha_hash" not in corpo


def test_cadastro_com_email_duplicado_da_409(client, admin):
    client.post(URL, json=NOVO_CLIENTE, headers=admin)

    resposta = client.post(URL, json=NOVO_CLIENTE, headers=admin)

    assert resposta.status_code == 409
    assert resposta.get_json()["erro"]["codigo"] == "CONFLITO"


@pytest.mark.parametrize("metodo", ["post", "put", "delete"])
def test_barbeiro_nao_escreve_cliente(client, barbeiro, metodo):
    cliente = criar_usuario(PAPEL_CLIENTE)
    url = URL if metodo == "post" else f"{URL}/{cliente.id}"

    resposta = getattr(client, metodo)(url, json=NOVO_CLIENTE, headers=barbeiro)

    assert resposta.status_code == 403


def test_cliente_logado_nao_lista_clientes(client, cliente_logado):
    assert client.get(URL, headers=cliente_logado).status_code == 403


def test_sem_token_da_401(client):
    resposta = client.get(URL)

    assert resposta.status_code == 401
    assert resposta.get_json()["erro"]["codigo"] == "NAO_AUTENTICADO"


def test_listagem_traz_so_clientes_e_pagina(client, barbeiro):
    for i in range(3):
        criar_usuario(PAPEL_CLIENTE, nome=f"Cliente {i}")
    criar_usuario(PAPEL_BARBEIRO, nome="Outro Barbeiro")

    resposta = client.get(f"{URL}?pagina=2&por_pagina=2", headers=barbeiro)

    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert corpo["total"] == 3
    assert corpo["paginas"] == 2
    assert corpo["pagina"] == 2
    assert [c["nome"] for c in corpo["itens"]] == ["Cliente 2"]


def test_busca_por_nome_ou_telefone(client, admin):
    criar_usuario(PAPEL_CLIENTE, nome="João Pereira", telefone="48911112222")
    criar_usuario(PAPEL_CLIENTE, nome="Ana Lima", telefone="48933334444")

    por_nome = client.get(f"{URL}?busca=joão", headers=admin).get_json()
    por_telefone = client.get(f"{URL}?busca=3333", headers=admin).get_json()

    assert [c["nome"] for c in por_nome["itens"]] == ["João Pereira"]
    assert [c["nome"] for c in por_telefone["itens"]] == ["Ana Lima"]


def test_busca_trata_curinga_como_texto(client, admin):
    criar_usuario(PAPEL_CLIENTE, nome="Ana Lima")

    corpo = client.get(f"{URL}?busca=%25", headers=admin).get_json()

    assert corpo["total"] == 0


def test_filtro_por_ativo(client, admin):
    criar_usuario(PAPEL_CLIENTE, nome="Ativo")
    criar_usuario(PAPEL_CLIENTE, nome="Inativo", ativo=False)

    corpo = client.get(f"{URL}?ativo=false", headers=admin).get_json()

    assert [c["nome"] for c in corpo["itens"]] == ["Inativo"]


def test_paginacao_invalida_da_422(client, admin):
    resposta = client.get(f"{URL}?por_pagina=500", headers=admin)

    assert resposta.status_code == 422
    assert "por_pagina" in resposta.get_json()["erro"]["campos"]


def test_detalhar_barbeiro_pela_rota_de_cliente_da_404(client, admin):
    outro = criar_usuario(PAPEL_BARBEIRO)

    assert client.get(f"{URL}/{outro.id}", headers=admin).status_code == 404


def test_atualizar_cliente(client, admin):
    cliente = criar_usuario(PAPEL_CLIENTE, telefone="111")

    resposta = client.put(
        f"{URL}/{cliente.id}", json={"nome": "Nome Novo"}, headers=admin
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["nome"] == "Nome Novo"
    assert resposta.get_json()["telefone"] == "111"


def test_atualizar_para_email_existente_da_409(client, admin):
    criar_usuario(PAPEL_CLIENTE, email="ocupado@exemplo.com")
    cliente = criar_usuario(PAPEL_CLIENTE)

    resposta = client.put(
        f"{URL}/{cliente.id}", json={"email": "ocupado@exemplo.com"}, headers=admin
    )

    assert resposta.status_code == 409


def test_atualizar_nao_aceita_trocar_papel(client, admin):
    cliente = criar_usuario(PAPEL_CLIENTE)

    resposta = client.put(f"{URL}/{cliente.id}", json={"papel": "admin"}, headers=admin)

    assert resposta.status_code == 422


def test_desativar_mantem_registro_e_impede_login(client, admin):
    cliente = criar_usuario(PAPEL_CLIENTE, email="sai@exemplo.com")

    resposta = client.delete(f"{URL}/{cliente.id}", headers=admin)

    assert resposta.status_code == 204
    db.session.expire_all()
    assert db.session.get(Usuario, cliente.id).ativo is False
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "sai@exemplo.com", "senha": "senha-boa-123"},
    )
    assert login.status_code == 401


def test_reativar_pelo_put(client, admin):
    cliente = criar_usuario(PAPEL_CLIENTE, ativo=False)

    resposta = client.put(f"{URL}/{cliente.id}", json={"ativo": True}, headers=admin)

    assert resposta.get_json()["ativo"] is True
