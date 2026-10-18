"""Service de agendamento, sem banco e sem subir o Flask.

Os testes de borda do conflito seguem o checklist do card da Fase 4. A agenda
de referencia tem um agendamento do barbeiro das 13:30 as 14:30.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.core.exceptions import Conflito, NaoEncontrado, RegraDeNegocioViolada
from app.core.fuso import FUSO_BARBEARIA
from app.models.agendamento import (
    STATUS_AGENDADO,
    STATUS_CANCELADO,
    STATUS_CONCLUIDO,
)
from app.models.servico import Servico
from app.models.usuario import PAPEL_ADMIN, PAPEL_BARBEIRO, PAPEL_CLIENTE, Usuario
from app.services.agendamento_service import (
    AgendamentoService,
    calcular_fim,
    intervalos_se_sobrepoem,
)
from app.services.servico_service import ServicoService


def hora(texto, dia=date(2026, 10, 20)):
    h, m = map(int, texto.split(":"))
    return datetime(dia.year, dia.month, dia.day, h, m, tzinfo=FUSO_BARBEARIA)


AGORA = hora("08:00")


class RepositorioAgendamentoFalso:
    def __init__(self):
        self.agendamentos = []
        self.proximo_id = 1

    def get_by_id(self, id):
        return next((a for a in self.agendamentos if a.id == id), None)

    def buscar_do_barbeiro_no_intervalo(self, barbeiro_id, inicio, fim):
        # De proposito devolve TODOS os do barbeiro, sem filtrar horario nem
        # status: assim o teste prova que a decisao esta no service.
        return [a for a in self.agendamentos if a.barbeiro_id == barbeiro_id]

    def listar(self, **filtros):
        self.ultimos_filtros = filtros
        return [], 0

    def create(self, entidade):
        entidade.id = self.proximo_id
        self.proximo_id += 1
        entidade.barbeiro_id = entidade.barbeiro.id
        entidade.cliente_id = entidade.cliente.id
        self.agendamentos.append(entidade)
        return entidade

    def update(self, entidade):
        entidade.barbeiro_id = entidade.barbeiro.id
        return entidade

    def desfazer(self):
        pass


class RepositorioServicoFalso:
    def __init__(self, servicos):
        self.servicos = servicos

    def buscar_por_ids(self, ids):
        return [s for s in self.servicos if s.id in ids]


class RepositorioUsuarioFalso:
    def __init__(self, usuarios):
        self.usuarios = {u.id: u for u in usuarios}

    def get_by_id(self, id):
        return self.usuarios.get(id)


def construir_usuario(id, papel, nome, ativo=True):
    usuario = Usuario(nome=nome, email=f"{id}@x.com", papel=papel, ativo=ativo)
    usuario.id = id
    return usuario


def construir_servico(id, nome, duracao, preco, ativo=True):
    servico = Servico(
        nome=nome, duracao_minutos=duracao, preco=Decimal(preco), ativo=ativo
    )
    servico.id = id
    return servico


ADMIN = construir_usuario(1, PAPEL_ADMIN, "Admin")
JOAO = construir_usuario(2, PAPEL_BARBEIRO, "João")
PEDRO = construir_usuario(3, PAPEL_BARBEIRO, "Pedro")
ANA = construir_usuario(4, PAPEL_CLIENTE, "Ana")
BIA = construir_usuario(5, PAPEL_CLIENTE, "Bia")
INATIVO = construir_usuario(6, PAPEL_BARBEIRO, "Velho", ativo=False)

CORTE = construir_servico(1, "Corte", 30, "35.00")
BARBA = construir_servico(2, "Barba", 20, "25.50")
SOBRANCELHA = construir_servico(3, "Sobrancelha", 10, "10.00")
LONGO = construir_servico(4, "Hora cheia", 60, "80.00")
ANTIGO = construir_servico(5, "Antigo", 30, "20.00", ativo=False)


@pytest.fixture
def repositorio():
    return RepositorioAgendamentoFalso()


@pytest.fixture
def service(repositorio):
    return AgendamentoService(
        repositorio,
        ServicoService(
            RepositorioServicoFalso([CORTE, BARBA, SOBRANCELHA, LONGO, ANTIGO])
        ),
        RepositorioUsuarioFalso([ADMIN, JOAO, PEDRO, ANA, BIA, INATIVO]),
        relogio=lambda: AGORA,
    )


def marcar(service, inicio, servicos=(LONGO,), barbeiro=JOAO, cliente=ANA,
           papel=PAPEL_ADMIN, usuario_id=ADMIN.id):
    dados = {
        "cliente_id": cliente.id,
        "barbeiro_id": barbeiro.id,
        "inicio": hora(inicio),
        "servico_ids": [s.id for s in servicos],
    }
    return service.criar(dados, usuario_id, papel)


@pytest.fixture
def existente(service):
    """O agendamento de referencia: 13:30 as 14:30 com o João."""
    return marcar(service, "13:30")


# --- calculo do fim (RF14) ---------------------------------------------------


def test_fim_e_inicio_mais_soma_das_duracoes():
    assert calcular_fim(hora("13:30"), [CORTE, BARBA]) == hora("14:20")


def test_fim_atravessa_meia_noite():
    fim = calcular_fim(hora("23:40"), [CORTE])
    assert fim == hora("00:10", dia=date(2026, 10, 21))


def test_criar_grava_fim_calculado(service):
    agendamento = marcar(service, "13:30", servicos=(CORTE, BARBA, SOBRANCELHA))
    assert agendamento.fim == hora("14:30")


# --- funcao pura de sobreposicao ---------------------------------------------


@pytest.mark.parametrize(
    "a, b, esperado",
    [
        (("13:00", "14:00"), ("14:00", "15:00"), False),  # encostados
        (("13:00", "14:00"), ("13:59", "15:00"), True),  # um minuto de folga
        (("13:00", "14:00"), ("12:00", "13:00"), False),
        (("13:00", "14:00"), ("13:00", "14:00"), True),
    ],
)
def test_intervalos_se_sobrepoem(a, b, esperado):
    assert intervalos_se_sobrepoem(hora(a[0]), hora(a[1]), hora(b[0]), hora(b[1])) is esperado


# --- checklist de borda do conflito (RN01) -------------------------------------


def test_permite_comecar_exatamente_quando_o_outro_termina(service, existente):
    agendamento = marcar(service, "14:30", servicos=(CORTE,))
    assert agendamento.inicio == existente.fim


def test_permite_terminar_exatamente_quando_o_outro_comeca(service, existente):
    agendamento = marcar(service, "13:00", servicos=(CORTE,))
    assert agendamento.fim == existente.inicio


def test_recusa_comecar_no_meio_de_um_existente(service, existente):
    with pytest.raises(Conflito):
        marcar(service, "14:00", servicos=(LONGO,))


def test_recusa_terminar_no_meio_de_um_existente(service, existente):
    with pytest.raises(Conflito):
        marcar(service, "13:00", servicos=(LONGO,))


def test_recusa_englobar_um_existente_por_inteiro(service, existente):
    # 13:00 ate 14:50 cobre todo o 13:30-14:30.
    with pytest.raises(Conflito):
        marcar(service, "13:00", servicos=(LONGO, CORTE, BARBA))


def test_recusa_ficar_inteiramente_dentro_de_um_existente(service, existente):
    with pytest.raises(Conflito):
        marcar(service, "13:45", servicos=(CORTE,))


def test_recusa_horario_identico_ao_de_um_existente(service, existente):
    with pytest.raises(Conflito):
        marcar(service, "13:30", servicos=(LONGO,))


def test_permite_mesmo_horario_com_barbeiro_diferente(service, existente):
    agendamento = marcar(service, "13:30", barbeiro=PEDRO)
    assert agendamento.barbeiro_id == PEDRO.id


def test_permite_remarcar_sem_mudar_o_horario(service, existente):
    remarcado = service.remarcar(
        existente.id, {"inicio": hora("13:30")}, ADMIN.id, PAPEL_ADMIN
    )
    assert (remarcado.inicio, remarcado.fim) == (hora("13:30"), hora("14:30"))


def test_permite_horario_ocupado_por_agendamento_cancelado(service, existente):
    service.cancelar(existente.id, ADMIN.id, PAPEL_ADMIN)
    agendamento = marcar(service, "13:30")
    assert agendamento.status == STATUS_AGENDADO


def test_concluido_continua_bloqueando_horario(service, existente):
    service.concluir(existente.id, ADMIN.id, PAPEL_ADMIN)
    with pytest.raises(Conflito):
        marcar(service, "13:30")


def test_mensagem_de_conflito_diz_quem_e_quando(service, existente):
    with pytest.raises(Conflito) as erro:
        marcar(service, "14:00")
    assert erro.value.mensagem == (
        "João já tem agendamento em 20/10/2026 das 13:30 às 14:30. "
        "Escolha outro horário."
    )


def test_conflito_compara_instantes_e_nao_o_relogio_local(service, existente):
    # 16:45 UTC = 13:45 em Brasilia: cai dentro do existente.
    inicio_utc = datetime(2026, 10, 20, 16, 45, tzinfo=timezone.utc)
    dados = {
        "cliente_id": ANA.id,
        "barbeiro_id": JOAO.id,
        "inicio": inicio_utc,
        "servico_ids": [CORTE.id],
    }
    with pytest.raises(Conflito):
        service.criar(dados, ADMIN.id, PAPEL_ADMIN)


# --- remarcar (RF18) -----------------------------------------------------------


def test_remarcar_para_frente_sobrepondo_o_proprio_horario_antigo(service, existente):
    remarcado = service.remarcar(
        existente.id, {"inicio": hora("14:00")}, ADMIN.id, PAPEL_ADMIN
    )
    assert (remarcado.inicio, remarcado.fim) == (hora("14:00"), hora("15:00"))


def test_remarcar_reaplica_a_regra_de_conflito(service, existente):
    outro = marcar(service, "16:00", cliente=BIA)
    with pytest.raises(Conflito):
        service.remarcar(outro.id, {"inicio": hora("14:00")}, ADMIN.id, PAPEL_ADMIN)
    assert outro.inicio == hora("16:00")


def test_remarcar_mantem_a_duracao_gravada(service, existente):
    # Mudar a duracao do servico depois nao desloca o agendamento (RN03).
    LONGO.duracao_minutos = 90
    try:
        remarcado = service.remarcar(
            existente.id, {"inicio": hora("15:00")}, ADMIN.id, PAPEL_ADMIN
        )
    finally:
        LONGO.duracao_minutos = 60
    assert remarcado.fim == hora("16:00")


def test_remarcar_para_outro_barbeiro_checa_a_agenda_dele(service, existente):
    marcar(service, "16:00", barbeiro=PEDRO, cliente=BIA)
    with pytest.raises(Conflito):
        service.remarcar(
            existente.id,
            {"inicio": hora("16:30"), "barbeiro_id": PEDRO.id},
            ADMIN.id,
            PAPEL_ADMIN,
        )


def test_remarcar_para_outro_barbeiro(service, existente):
    remarcado = service.remarcar(
        existente.id,
        {"inicio": hora("13:30"), "barbeiro_id": PEDRO.id},
        ADMIN.id,
        PAPEL_ADMIN,
    )
    assert remarcado.barbeiro_id == PEDRO.id


@pytest.mark.parametrize("acao", ["cancelar", "concluir"])
def test_so_agendado_pode_ser_remarcado(service, existente, acao):
    getattr(service, acao)(existente.id, ADMIN.id, PAPEL_ADMIN)
    with pytest.raises(RegraDeNegocioViolada):
        service.remarcar(existente.id, {"inicio": hora("16:00")}, ADMIN.id, PAPEL_ADMIN)


# --- transicoes de status --------------------------------------------------------


def test_cancelar_mantem_o_registro(service, repositorio, existente):
    service.cancelar(existente.id, ADMIN.id, PAPEL_ADMIN)
    assert repositorio.get_by_id(existente.id).status == STATUS_CANCELADO


@pytest.mark.parametrize(
    "primeira, segunda",
    [
        ("concluir", "cancelar"),
        ("cancelar", "concluir"),
        ("cancelar", "cancelar"),
        ("concluir", "concluir"),
    ],
)
def test_status_final_nao_muda_mais(service, existente, primeira, segunda):
    getattr(service, primeira)(existente.id, ADMIN.id, PAPEL_ADMIN)
    with pytest.raises(RegraDeNegocioViolada):
        getattr(service, segunda)(existente.id, ADMIN.id, PAPEL_ADMIN)


def test_mensagem_de_transicao_invalida(service, existente):
    service.concluir(existente.id, ADMIN.id, PAPEL_ADMIN)
    with pytest.raises(RegraDeNegocioViolada) as erro:
        service.cancelar(existente.id, ADMIN.id, PAPEL_ADMIN)
    assert erro.value.mensagem == (
        "Agendamento concluído não pode ser marcado como cancelado."
    )
    assert existente.status == STATUS_CONCLUIDO


# --- criacao: precos, validacoes e papeis ---------------------------------------


def test_preco_cobrado_e_copiado_do_servico(service):
    agendamento = marcar(service, "10:00", servicos=(CORTE, BARBA))
    assert [i.preco_cobrado for i in agendamento.itens] == [
        Decimal("35.00"),
        Decimal("25.50"),
    ]


def test_recusa_horario_no_passado(service):
    with pytest.raises(RegraDeNegocioViolada):
        marcar(service, "07:59")


def test_recusa_servico_desativado(service):
    with pytest.raises(RegraDeNegocioViolada):
        marcar(service, "10:00", servicos=(CORTE, ANTIGO))


def test_recusa_barbeiro_desativado(service):
    with pytest.raises(RegraDeNegocioViolada):
        marcar(service, "10:00", barbeiro=INATIVO)


@pytest.mark.parametrize(
    "barbeiro, cliente",
    [(ANA, ANA), (JOAO, JOAO), (construir_usuario(99, PAPEL_BARBEIRO, "X"), ANA)],
)
def test_barbeiro_e_cliente_precisam_existir_com_o_papel_certo(service, barbeiro, cliente):
    with pytest.raises(NaoEncontrado):
        marcar(service, "10:00", barbeiro=barbeiro, cliente=cliente)


def test_cliente_marca_sempre_para_si_mesmo(service):
    agendamento = marcar(
        service, "10:00", cliente=BIA, papel=PAPEL_CLIENTE, usuario_id=ANA.id
    )
    assert agendamento.cliente_id == ANA.id


# --- visibilidade do cliente (RF21) ---------------------------------------------


def test_cliente_nao_enxerga_agendamento_de_outro(service, existente):
    with pytest.raises(NaoEncontrado):
        service.buscar(existente.id, BIA.id, PAPEL_CLIENTE)
    with pytest.raises(NaoEncontrado):
        service.cancelar(existente.id, BIA.id, PAPEL_CLIENTE)


def test_cliente_cancela_o_proprio(service, existente):
    cancelado = service.cancelar(existente.id, ANA.id, PAPEL_CLIENTE)
    assert cancelado.status == STATUS_CANCELADO


def test_listagem_do_cliente_e_forcada_para_ele(service, repositorio):
    service.listar(ANA.id, PAPEL_CLIENTE, cliente_id=BIA.id)
    assert repositorio.ultimos_filtros["cliente_id"] == ANA.id


def test_listagem_por_dia_usa_o_dia_de_brasilia(service, repositorio):
    service.listar(ADMIN.id, PAPEL_ADMIN, dia=date(2026, 10, 20))
    assert repositorio.ultimos_filtros["inicio"] == hora("00:00")
    assert repositorio.ultimos_filtros["fim"] - repositorio.ultimos_filtros[
        "inicio"
    ] == timedelta(days=1)
