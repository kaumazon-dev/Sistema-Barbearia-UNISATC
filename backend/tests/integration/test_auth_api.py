from app.models.usuario import PAPEL_BARBEIRO, PAPEL_CLIENTE
from tests.integration.fabricas import criar_usuario

URL_BARBEIROS = "/api/v1/auth/barbeiros"


def test_cliente_lista_barbeiros_ativos_so_com_id_e_nome(client, cliente_logado):
    joao = criar_usuario(PAPEL_BARBEIRO, nome="João", telefone="48999990000")
    criar_usuario(PAPEL_BARBEIRO, nome="Pedro", ativo=False)
    criar_usuario(PAPEL_CLIENTE, nome="Ana")

    resposta = client.get(URL_BARBEIROS, headers=cliente_logado)

    assert resposta.status_code == 200
    assert resposta.get_json() == [{"id": joao.id, "nome": "João"}]


def test_barbeiros_vem_em_ordem_de_nome(client, barbeiro):
    criar_usuario(PAPEL_BARBEIRO, nome="Zeca")
    criar_usuario(PAPEL_BARBEIRO, nome="Bruno")

    resposta = client.get(URL_BARBEIROS, headers=barbeiro)

    nomes = [item["nome"] for item in resposta.get_json()]
    assert nomes == sorted(nomes)


def test_barbeiros_sem_token_da_401(client):
    resposta = client.get(URL_BARBEIROS)

    assert resposta.status_code == 401
    assert resposta.get_json()["erro"]["codigo"] == "NAO_AUTENTICADO"
