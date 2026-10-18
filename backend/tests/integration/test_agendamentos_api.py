from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.fuso import FUSO_BARBEARIA
from app.extensions import db
from app.models.agendamento import Agendamento
from app.models.servico import Servico
from app.models.usuario import PAPEL_BARBEIRO, PAPEL_CLIENTE
from app.repositories.agendamento_repository import AgendamentoRepository
from tests.integration.fabricas import cabecalho_de, criar_usuario

URL = "/api/v1/agendamentos"

# Sempre no futuro, para nao esbarrar na regra de horario no passado.
DIA = (datetime.now(FUSO_BARBEARIA) + timedelta(days=7)).date()


def hora(texto):
    h, m = map(int, texto.split(":"))
    return datetime(DIA.year, DIA.month, DIA.day, h, m, tzinfo=FUSO_BARBEARIA)


def criar_servico(nome="Corte", duracao=30, preco="35.00"):
    servico = Servico(nome=nome, duracao_minutos=duracao, preco=Decimal(preco))
    db.session.add(servico)
    db.session.commit()
    return servico


@pytest.fixture
def cenario():
    return {
        "joao": criar_usuario(PAPEL_BARBEIRO, nome="João"),
        "pedro": criar_usuario(PAPEL_BARBEIRO, nome="Pedro"),
        "ana": criar_usuario(PAPEL_CLIENTE, nome="Ana"),
        "bia": criar_usuario(PAPEL_CLIENTE, nome="Bia"),
        "corte": criar_servico("Corte", 30, "35.00"),
        "barba": criar_servico("Barba", 30, "25.50"),
    }


def corpo(cenario, inicio, barbeiro="joao", cliente="ana", servicos=("corte", "barba")):
    return {
        "cliente_id": cenario[cliente].id,
        "barbeiro_id": cenario[barbeiro].id,
        "inicio": hora(inicio).isoformat(),
        "servico_ids": [cenario[s].id for s in servicos],
    }


def marcar(client, cabecalho, cenario, inicio, **kwargs):
    return client.post(URL, json=corpo(cenario, inicio, **kwargs), headers=cabecalho)


def test_cria_com_fim_calculado_e_preco_congelado(client, admin, cenario):
    resposta = marcar(client, admin, cenario, "13:30")

    assert resposta.status_code == 201
    agendamento = resposta.get_json()
    assert agendamento["inicio"] == hora("13:30").isoformat()
    assert agendamento["fim"] == hora("14:30").isoformat()
    assert agendamento["status"] == "agendado"
    assert agendamento["total"] == "60.50"
    assert agendamento["barbeiro"] == {"id": cenario["joao"].id, "nome": "João"}

    # Mudar o preco depois nao altera o que ja foi marcado (RN02).
    cenario["corte"].preco = Decimal("99.00")
    db.session.commit()
    detalhe = client.get(f"{URL}/{agendamento['id']}", headers=admin).get_json()
    assert [s["preco_cobrado"] for s in detalhe["servicos"]] == ["35.00", "25.50"]


def test_conflito_responde_409_com_mensagem_para_a_tela(client, admin, cenario):
    marcar(client, admin, cenario, "13:30")

    resposta = marcar(client, admin, cenario, "14:00", cliente="bia")

    assert resposta.status_code == 409
    erro = resposta.get_json()["erro"]
    assert erro["codigo"] == "CONFLITO"
    assert "João já tem agendamento" in erro["mensagem"]
    assert "das 13:30 às 14:30" in erro["mensagem"]


def test_encostado_e_barbeiro_diferente_sao_aceitos(client, admin, cenario):
    marcar(client, admin, cenario, "13:30")

    depois = marcar(client, admin, cenario, "14:30", cliente="bia")
    antes = marcar(client, admin, cenario, "12:30", cliente="bia")
    outro_barbeiro = marcar(client, admin, cenario, "13:30", barbeiro="pedro", cliente="bia")

    assert [depois.status_code, antes.status_code, outro_barbeiro.status_code] == [201, 201, 201]


def test_cancelado_libera_o_horario(client, admin, cenario):
    id_ = marcar(client, admin, cenario, "13:30").get_json()["id"]

    cancelado = client.post(f"{URL}/{id_}/cancelar", headers=admin)
    novo = marcar(client, admin, cenario, "13:30", cliente="bia")

    assert cancelado.get_json()["status"] == "cancelado"
    assert novo.status_code == 201


def test_remarcar_e_concluir(client, admin, cenario):
    id_ = marcar(client, admin, cenario, "13:30").get_json()["id"]

    remarcado = client.patch(
        f"{URL}/{id_}", json={"inicio": hora("14:00").isoformat()}, headers=admin
    )
    concluido = client.post(f"{URL}/{id_}/concluir", headers=admin)
    cancelar_concluido = client.post(f"{URL}/{id_}/cancelar", headers=admin)

    assert remarcado.status_code == 200
    assert remarcado.get_json()["fim"] == hora("15:00").isoformat()
    assert concluido.get_json()["status"] == "concluido"
    assert cancelar_concluido.status_code == 422
    assert cancelar_concluido.get_json()["erro"]["codigo"] == "REGRA_VIOLADA"


def test_remarcar_para_horario_ocupado_da_409(client, admin, cenario):
    marcar(client, admin, cenario, "13:30")
    id_ = marcar(client, admin, cenario, "16:00", cliente="bia").get_json()["id"]

    resposta = client.patch(
        f"{URL}/{id_}", json={"inicio": hora("14:00").isoformat()}, headers=admin
    )

    assert resposta.status_code == 409


def test_lista_por_dia_e_barbeiro(client, admin, cenario):
    marcar(client, admin, cenario, "15:00")
    marcar(client, admin, cenario, "09:00", cliente="bia")
    marcar(client, admin, cenario, "09:00", barbeiro="pedro")

    do_joao = client.get(
        f"{URL}?dia={DIA.isoformat()}&barbeiro_id={cenario['joao'].id}", headers=admin
    ).get_json()
    outro_dia = client.get(
        f"{URL}?dia={(DIA + timedelta(days=1)).isoformat()}", headers=admin
    ).get_json()

    assert do_joao["total"] == 2
    assert [a["inicio"] for a in do_joao["itens"]] == [
        hora("09:00").isoformat(),
        hora("15:00").isoformat(),
    ]
    assert outro_dia["total"] == 0


def test_dia_de_brasilia_inclui_a_noite_que_em_utc_ja_e_amanha(client, admin, cenario):
    # 22:00 em Brasilia e 01:00 UTC do dia seguinte.
    marcar(client, admin, cenario, "22:00", servicos=("corte",))

    lista = client.get(f"{URL}?dia={DIA.isoformat()}", headers=admin).get_json()

    assert lista["total"] == 1


def test_cliente_marca_para_si_e_so_ve_os_proprios(client, admin, cenario):
    ana = cabecalho_de(cenario["ana"])
    marcar(client, admin, cenario, "09:00", cliente="bia")

    # cliente_id da Bia no corpo e ignorado: a Ana marca para ela mesma.
    propria = marcar(client, ana, cenario, "13:30", cliente="bia")
    lista = client.get(URL, headers=ana).get_json()

    assert propria.status_code == 201
    assert propria.get_json()["cliente"]["id"] == cenario["ana"].id
    assert [a["cliente"]["nome"] for a in lista["itens"]] == ["Ana"]


def test_cliente_nao_acessa_agendamento_de_outro(client, admin, cenario):
    id_ = marcar(client, admin, cenario, "09:00", cliente="bia").get_json()["id"]
    ana = cabecalho_de(cenario["ana"])

    assert client.get(f"{URL}/{id_}", headers=ana).status_code == 404
    assert client.post(f"{URL}/{id_}/cancelar", headers=ana).status_code == 404
    assert client.post(f"{URL}/{id_}/concluir", headers=ana).status_code == 403


def test_admin_precisa_informar_cliente(client, admin, cenario):
    dados = corpo(cenario, "09:00")
    del dados["cliente_id"]

    resposta = client.post(URL, json=dados, headers=admin)

    assert resposta.status_code == 422
    assert "cliente_id" in resposta.get_json()["erro"]["campos"]


def test_horario_sem_fuso_da_422(client, admin, cenario):
    dados = dict(corpo(cenario, "09:00"), inicio=f"{DIA.isoformat()}T09:00:00")

    resposta = client.post(URL, json=dados, headers=admin)

    assert resposta.status_code == 422
    assert "inicio" in resposta.get_json()["erro"]["campos"]


def test_sem_token_da_401(client):
    assert client.get(URL).status_code == 401


# --- rede de seguranca do banco contra condicao de corrida ---------------------


def test_banco_recusa_sobreposicao_mesmo_sem_o_service(cenario):
    def agendamento(inicio, fim):
        return Agendamento(
            cliente_id=cenario["ana"].id,
            barbeiro_id=cenario["joao"].id,
            inicio=hora(inicio),
            fim=hora(fim),
        )

    db.session.add(agendamento("13:30", "14:30"))
    db.session.commit()
    db.session.add(agendamento("14:30", "15:00"))  # encostado: o banco aceita
    db.session.commit()

    db.session.add(agendamento("14:00", "14:45"))
    with pytest.raises(IntegrityError) as erro:
        db.session.commit()
    db.session.rollback()
    assert erro.value.orig.pgcode == "23P01"


def test_corrida_entre_checagem_e_commit_vira_409(client, admin, cenario, monkeypatch):
    marcar(client, admin, cenario, "13:30")
    # Simula a outra requisicao: a checagem do service nao enxerga o existente,
    # como aconteceria se os dois commits fossem simultaneos.
    monkeypatch.setattr(
        AgendamentoRepository, "buscar_do_barbeiro_no_intervalo", lambda *a: []
    )

    resposta = marcar(client, admin, cenario, "14:00", cliente="bia")

    assert resposta.status_code == 409
    assert "acabou de ser ocupado" in resposta.get_json()["erro"]["mensagem"]
    assert db.session.query(Agendamento).count() == 1


def test_horarios_sao_gravados_com_fuso(client, admin, cenario):
    id_ = marcar(client, admin, cenario, "13:30").get_json()["id"]
    db.session.expire_all()

    gravado = db.session.get(Agendamento, id_)

    assert gravado.inicio == hora("13:30")
    assert gravado.inicio.utcoffset() is not None
    assert gravado.inicio.astimezone(timezone.utc).hour == 16
