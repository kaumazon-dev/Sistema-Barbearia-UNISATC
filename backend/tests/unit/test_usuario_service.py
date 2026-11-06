"""UsuarioService.alterar_papel, sem banco: repositorios falsos."""

from datetime import datetime, timezone

import pytest

from app.core.exceptions import NaoEncontrado, RegraDeNegocioViolada
from app.models.agendamento import STATUS_AGENDADO
from app.models.usuario import PAPEL_ADMIN, PAPEL_BARBEIRO, PAPEL_CLIENTE, Usuario
from app.services.usuario_service import UsuarioService

AGORA = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)


class RepositorioUsuarioFalso:
    def __init__(self, usuarios):
        self.usuarios = {u.id: u for u in usuarios}
        self.atualizados = []

    def get_by_id(self, id):
        return self.usuarios.get(id)

    def update(self, entidade):
        self.atualizados.append(entidade)
        return entidade


class RepositorioAgendamentoFalso:
    def __init__(self, pendentes=0):
        self.pendentes = pendentes
        self.chamadas = []

    def contar_do_barbeiro_a_partir_de(self, barbeiro_id, instante, status):
        self.chamadas.append((barbeiro_id, instante, status))
        return self.pendentes


def usuario(id, papel, nome="Fulano"):
    u = Usuario(nome=nome, email=f"{id}@x.com", papel=papel, ativo=True)
    u.id = id
    return u


def montar(*usuarios, pendentes=0):
    usuarios_repo = RepositorioUsuarioFalso(usuarios)
    agenda_repo = RepositorioAgendamentoFalso(pendentes)
    service = UsuarioService(usuarios_repo, agenda_repo, relogio=lambda: AGORA)
    return service, usuarios_repo, agenda_repo


ADMIN_ID = 1


@pytest.mark.parametrize("novo", [PAPEL_BARBEIRO, PAPEL_ADMIN])
def test_admin_promove_cliente(novo):
    ana = usuario(2, PAPEL_CLIENTE)
    service, repo, _ = montar(ana)

    resultado = service.alterar_papel(2, novo, admin_id=ADMIN_ID)

    assert resultado.papel == novo
    assert repo.atualizados == [ana]


def test_admin_nao_altera_o_proprio_papel():
    """Garante que sempre sobra pelo menos um admin."""
    eu = usuario(ADMIN_ID, PAPEL_ADMIN)
    service, repo, _ = montar(eu)

    with pytest.raises(RegraDeNegocioViolada) as erro:
        service.alterar_papel(ADMIN_ID, PAPEL_CLIENTE, admin_id=ADMIN_ID)

    assert "próprio papel" in erro.value.mensagem
    assert eu.papel == PAPEL_ADMIN
    assert repo.atualizados == []


def test_admin_rebaixa_outro_admin():
    outro = usuario(2, PAPEL_ADMIN)
    service, _, _ = montar(outro)

    assert service.alterar_papel(2, PAPEL_CLIENTE, admin_id=ADMIN_ID).papel == PAPEL_CLIENTE


def test_usuario_inexistente():
    service, _, _ = montar()

    with pytest.raises(NaoEncontrado):
        service.alterar_papel(99, PAPEL_BARBEIRO, admin_id=ADMIN_ID)


def test_papel_invalido_recusa():
    service, _, _ = montar(usuario(2, PAPEL_CLIENTE))

    with pytest.raises(RegraDeNegocioViolada):
        service.alterar_papel(2, "dono", admin_id=ADMIN_ID)


def test_mesmo_papel_nao_grava_nada():
    service, repo, _ = montar(usuario(2, PAPEL_BARBEIRO))

    service.alterar_papel(2, PAPEL_BARBEIRO, admin_id=ADMIN_ID)

    assert repo.atualizados == []


def test_barbeiro_com_horario_marcado_continua_barbeiro():
    joao = usuario(2, PAPEL_BARBEIRO, nome="João")
    service, repo, agenda = montar(joao, pendentes=3)

    with pytest.raises(RegraDeNegocioViolada) as erro:
        service.alterar_papel(2, PAPEL_CLIENTE, admin_id=ADMIN_ID)

    assert erro.value.mensagem.startswith("João ainda tem 3 horários marcados.")
    assert joao.papel == PAPEL_BARBEIRO
    assert repo.atualizados == []
    # A pergunta ao repositorio e "agendados de agora em diante".
    assert agenda.chamadas == [(2, AGORA, STATUS_AGENDADO)]


def test_mensagem_no_singular_com_um_horario():
    service, _, _ = montar(usuario(2, PAPEL_BARBEIRO, nome="João"), pendentes=1)

    with pytest.raises(RegraDeNegocioViolada) as erro:
        service.alterar_papel(2, PAPEL_ADMIN, admin_id=ADMIN_ID)

    assert "1 horário marcado." in erro.value.mensagem


def test_barbeiro_sem_horario_futuro_pode_mudar():
    joao = usuario(2, PAPEL_BARBEIRO)
    service, _, _ = montar(joao, pendentes=0)

    assert service.alterar_papel(2, PAPEL_ADMIN, admin_id=ADMIN_ID).papel == PAPEL_ADMIN


def test_cliente_nao_consulta_a_agenda():
    """A checagem de agenda so existe para quem deixa de ser barbeiro."""
    service, _, agenda = montar(usuario(2, PAPEL_CLIENTE))

    service.alterar_papel(2, PAPEL_BARBEIRO, admin_id=ADMIN_ID)

    assert agenda.chamadas == []
