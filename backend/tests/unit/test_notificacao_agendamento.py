"""Aviso por e-mail de agendamento criado, sem banco e sem Flask."""

from datetime import datetime, timezone
from decimal import Decimal

from app.core.fuso import FUSO_BARBEARIA
from app.models.agendamento import Agendamento, AgendamentoServico
from app.models.servico import Servico
from app.models.usuario import PAPEL_BARBEIRO, PAPEL_CLIENTE, Usuario
from app.services.notificacao_agendamento import (
    ASSUNTO_BARBEIRO,
    ASSUNTO_CLIENTE,
    NotificadorAgendamento,
)


class EnviadorFalso:
    def __init__(self, falhar=False):
        self.enviados = []
        self.falhar = falhar

    def enviar(self, para, assunto, corpo):
        if self.falhar:
            raise OSError("SMTP fora do ar")
        self.enviados.append({"para": para, "assunto": assunto, "corpo": corpo})


def agendamento(observacao=None):
    corte = Servico(nome="Corte", duracao_minutos=30, preco=Decimal("35.00"))
    barba = Servico(nome="Barba", duracao_minutos=30, preco=Decimal("25.50"))
    return Agendamento(
        cliente=Usuario(nome="Ana", email="ana@x.com", papel=PAPEL_CLIENTE),
        barbeiro=Usuario(nome="João", email="joao@x.com", papel=PAPEL_BARBEIRO),
        inicio=datetime(2026, 10, 20, 13, 30, tzinfo=FUSO_BARBEARIA),
        fim=datetime(2026, 10, 20, 14, 30, tzinfo=FUSO_BARBEARIA),
        observacao=observacao,
        itens=[
            AgendamentoServico(servico=corte, preco_cobrado=Decimal("35.00")),
            AgendamentoServico(servico=barba, preco_cobrado=Decimal("25.50")),
        ],
    )


def test_avisa_cliente_e_barbeiro():
    enviador = EnviadorFalso()
    NotificadorAgendamento(enviador).agendamento_criado(agendamento())

    cliente, barbeiro = enviador.enviados
    assert (cliente["para"], cliente["assunto"]) == ("ana@x.com", ASSUNTO_CLIENTE)
    assert (barbeiro["para"], barbeiro["assunto"]) == ("joao@x.com", ASSUNTO_BARBEIRO)
    assert "com João" in cliente["corpo"]
    assert "Ana marcou" in barbeiro["corpo"]


def test_corpo_traz_data_hora_servicos_e_total():
    enviador = EnviadorFalso()
    NotificadorAgendamento(enviador).agendamento_criado(agendamento())

    corpo = enviador.enviados[0]["corpo"]
    assert "Data: 20/10/2026" in corpo
    assert "Horário: 13:30 às 14:30" in corpo
    assert "Serviços: Corte, Barba" in corpo
    assert "Total: R$ 60,50" in corpo
    assert "Observação" not in corpo


def test_hora_sai_no_fuso_da_barbearia_mesmo_vindo_em_utc():
    item = agendamento()
    item.inicio = item.inicio.astimezone(timezone.utc)
    item.fim = item.fim.astimezone(timezone.utc)
    enviador = EnviadorFalso()
    NotificadorAgendamento(enviador).agendamento_criado(item)

    assert "Horário: 13:30 às 14:30" in enviador.enviados[0]["corpo"]


def test_inclui_observacao_quando_houver():
    enviador = EnviadorFalso()
    NotificadorAgendamento(enviador).agendamento_criado(agendamento("Só máquina 2"))

    assert "Observação: Só máquina 2" in enviador.enviados[0]["corpo"]


def test_falha_no_envio_nao_estoura():
    NotificadorAgendamento(EnviadorFalso(falhar=True)).agendamento_criado(agendamento())
