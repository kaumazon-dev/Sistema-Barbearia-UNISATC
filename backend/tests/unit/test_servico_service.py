"""Service de servico, sem banco e sem subir o Flask."""

from decimal import Decimal

import pytest

from app.core.exceptions import NaoEncontrado, RegraDeNegocioViolada
from app.models.servico import Servico
from app.services.servico_service import ServicoService


class RepositorioFalso:
    def __init__(self, servicos=None):
        self.servicos = list(servicos or [])
        self.proximo_id = len(self.servicos) + 1

    def get_by_id(self, id):
        return next((s for s in self.servicos if s.id == id), None)

    def buscar_por_ids(self, ids):
        return [s for s in self.servicos if s.id in ids]

    def create(self, entidade):
        entidade.id = self.proximo_id
        self.proximo_id += 1
        self.servicos.append(entidade)
        return entidade

    def update(self, entidade):
        return entidade


def construir_servico(id, nome="Corte", ativo=True):
    servico = Servico(
        nome=nome, duracao_minutos=30, preco=Decimal("35.00"), ativo=ativo
    )
    servico.id = id
    return servico


def test_cadastrar_guarda_preco_como_decimal():
    servico = ServicoService(RepositorioFalso()).cadastrar(
        {"nome": "Corte", "duracao_minutos": 30, "preco": Decimal("35.90")}
    )

    assert servico.id == 1
    assert isinstance(servico.preco, Decimal)


def test_buscar_inexistente_recusa():
    with pytest.raises(NaoEncontrado):
        ServicoService(RepositorioFalso()).buscar(1)


def test_atualizar_altera_so_os_campos_enviados():
    existente = construir_servico(1)
    servico = ServicoService(RepositorioFalso([existente]))

    servico.atualizar(1, {"preco": Decimal("40.00")})

    assert existente.preco == Decimal("40.00")
    assert existente.duracao_minutos == 30
    assert existente.nome == "Corte"


def test_desativar_nao_apaga_so_marca_inativo():
    existente = construir_servico(1)
    repositorio = RepositorioFalso([existente])

    ServicoService(repositorio).desativar(1)

    assert existente.ativo is False
    assert existente in repositorio.servicos


def test_agendamento_recebe_servicos_ativos_na_ordem_pedida():
    corte, barba = construir_servico(1, "Corte"), construir_servico(2, "Barba")
    servico = ServicoService(RepositorioFalso([corte, barba]))

    assert servico.buscar_ativos_para_agendamento([2, 1, 2]) == [barba, corte]


def test_agendamento_com_servico_desativado_recusa():
    """RF12: servico desativado nao entra em agendamento novo."""
    servico = ServicoService(
        RepositorioFalso([construir_servico(1), construir_servico(2, "Barba", ativo=False)])
    )

    with pytest.raises(RegraDeNegocioViolada, match="Barba"):
        servico.buscar_ativos_para_agendamento([1, 2])


def test_agendamento_com_servico_inexistente_recusa():
    servico = ServicoService(RepositorioFalso([construir_servico(1)]))

    with pytest.raises(NaoEncontrado, match="7"):
        servico.buscar_ativos_para_agendamento([1, 7])
