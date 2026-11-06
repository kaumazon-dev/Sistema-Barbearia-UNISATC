from datetime import timedelta

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import Conflito, NaoEncontrado, RegraDeNegocioViolada
from app.core.fuso import FUSO_BARBEARIA, agora, intervalo_do_dia
from app.models.agendamento import (
    STATUS_AGENDADO,
    STATUS_CANCELADO,
    STATUS_CONCLUIDO,
    Agendamento,
    AgendamentoServico,
)
from app.models.usuario import PAPEL_BARBEIRO, PAPEL_CLIENTE

# Transicoes validas de status. Concluido e cancelado sao finais: cancelar
# muda o status e mantem o registro, senao o dashboard perde a taxa de
# cancelamento (RF19).
TRANSICOES = {
    STATUS_AGENDADO: {STATUS_CONCLUIDO, STATUS_CANCELADO},
    STATUS_CONCLUIDO: set(),
    STATUS_CANCELADO: set(),
}

_NOME_STATUS = {
    STATUS_AGENDADO: "agendado",
    STATUS_CONCLUIDO: "concluído",
    STATUS_CANCELADO: "cancelado",
}

# SQLSTATE do Postgres para violacao de EXCLUDE constraint.
_VIOLACAO_EXCLUSAO = "23P01"


def calcular_fim(inicio, servicos):
    """fim = inicio + soma das duracoes dos servicos (RF14)."""
    return inicio + timedelta(minutes=sum(s.duracao_minutos for s in servicos))


def intervalos_se_sobrepoem(inicio_a, fim_a, inicio_b, fim_b):
    """[inicio_a, fim_a) e [inicio_b, fim_b) se sobrepoem? (RN01)

    `<` e nao `<=`: o intervalo e aberto no fim, entao um agendamento que
    comeca exatamente quando o outro termina nao conflita.
    """
    return inicio_a < fim_b and fim_a > inicio_b


class AgendamentoService:
    """Quem esta logado chega por argumento (usuario_id, papel), vindo da rota.

    Cliente so enxerga e mexe nos proprios agendamentos (RF21): para ele, o
    agendamento de outra pessoa simplesmente nao existe.
    """

    def __init__(self, repositorio, servico_service, usuario_repositorio, relogio=agora):
        self.repositorio = repositorio
        self.servico_service = servico_service
        self.usuario_repositorio = usuario_repositorio
        self.relogio = relogio

    def listar(self, usuario_id, papel, dia=None, barbeiro_id=None, cliente_id=None,
               status=None, pagina=1, por_pagina=20):
        if papel == PAPEL_CLIENTE:
            cliente_id = usuario_id
        inicio, fim = intervalo_do_dia(dia) if dia is not None else (None, None)
        return self.repositorio.listar(
            inicio=inicio,
            fim=fim,
            barbeiro_id=barbeiro_id,
            cliente_id=cliente_id,
            status=status,
            pagina=pagina,
            por_pagina=por_pagina,
        )

    def buscar(self, agendamento_id, usuario_id, papel):
        agendamento = self.repositorio.get_by_id(agendamento_id)
        if agendamento is None or (
            papel == PAPEL_CLIENTE and agendamento.cliente_id != usuario_id
        ):
            raise NaoEncontrado(f"Agendamento {agendamento_id} não existe.")
        return agendamento

    def criar(self, dados, usuario_id, papel):
        # Cliente sempre marca para si mesmo, o que vier no corpo e ignorado.
        cliente_id = usuario_id if papel == PAPEL_CLIENTE else dados["cliente_id"]
        cliente = self._usuario_ativo(cliente_id, PAPEL_CLIENTE, "Cliente")
        barbeiro = self._usuario_ativo(dados["barbeiro_id"], PAPEL_BARBEIRO, "Barbeiro")
        servicos = self.servico_service.buscar_ativos_para_agendamento(
            dados["servico_ids"]
        )

        inicio = dados["inicio"]
        fim = calcular_fim(inicio, servicos)
        self._validar_futuro(inicio)
        self._garantir_horario_livre(barbeiro, inicio, fim)

        agendamento = Agendamento(
            cliente=cliente,
            barbeiro=barbeiro,
            inicio=inicio,
            fim=fim,
            status=STATUS_AGENDADO,
            observacao=dados.get("observacao"),
            itens=[
                # Preco congelado na marcacao (RN02).
                AgendamentoServico(servico=s, preco_cobrado=s.preco) for s in servicos
            ],
        )
        return self._gravar(self.repositorio.create, agendamento, barbeiro)

    def remarcar(self, agendamento_id, dados, usuario_id, papel):
        """Novo inicio (e opcionalmente outro barbeiro), mesma duracao.

        A duracao vem do proprio agendamento e nao dos servicos: mudar a duracao
        de um servico depois da marcacao nao altera este agendamento (RN03).
        """
        agendamento = self.buscar(agendamento_id, usuario_id, papel)
        if agendamento.status != STATUS_AGENDADO:
            raise RegraDeNegocioViolada(
                f"Agendamento {_NOME_STATUS[agendamento.status]} não pode ser remarcado."
            )

        barbeiro = agendamento.barbeiro
        if dados.get("barbeiro_id", barbeiro.id) != barbeiro.id:
            barbeiro = self._usuario_ativo(
                dados["barbeiro_id"], PAPEL_BARBEIRO, "Barbeiro"
            )

        inicio = dados["inicio"]
        fim = inicio + (agendamento.fim - agendamento.inicio)
        self._validar_futuro(inicio)
        # Sem ignorar o proprio id, remarcar 15 min para frente conflitaria
        # com o horario antigo dele mesmo (RF18).
        self._garantir_horario_livre(barbeiro, inicio, fim, ignorar_id=agendamento.id)

        agendamento.barbeiro = barbeiro
        agendamento.inicio = inicio
        agendamento.fim = fim
        return self._gravar(self.repositorio.update, agendamento, barbeiro)

    def cancelar(self, agendamento_id, usuario_id, papel):
        agendamento = self.buscar(agendamento_id, usuario_id, papel)
        return self._mudar_status(agendamento, STATUS_CANCELADO)

    def concluir(self, agendamento_id, usuario_id, papel):
        agendamento = self.buscar(agendamento_id, usuario_id, papel)
        return self._mudar_status(agendamento, STATUS_CONCLUIDO)

    def _mudar_status(self, agendamento, novo_status):
        if novo_status not in TRANSICOES[agendamento.status]:
            raise RegraDeNegocioViolada(
                f"Agendamento {_NOME_STATUS[agendamento.status]} não pode ser "
                f"marcado como {_NOME_STATUS[novo_status]}."
            )
        agendamento.status = novo_status
        return self.repositorio.update(agendamento)

    def _usuario_ativo(self, usuario_id, papel, rotulo):
        usuario = self.usuario_repositorio.get_by_id(usuario_id)
        if usuario is None or usuario.papel != papel:
            raise NaoEncontrado(f"{rotulo} {usuario_id} não existe.")
        if not usuario.ativo:
            raise RegraDeNegocioViolada(f"{rotulo} {usuario.nome} está desativado.")
        return usuario

    def _validar_futuro(self, inicio):
        if inicio < self.relogio():
            raise RegraDeNegocioViolada("Não é possível agendar um horário no passado.")

    def _garantir_horario_livre(self, barbeiro, inicio, fim, ignorar_id=None):
        """RN01: nenhum agendamento do mesmo barbeiro pode se sobrepor."""
        candidatos = self.repositorio.buscar_do_barbeiro_no_intervalo(
            barbeiro.id, inicio, fim
        )
        for outro in candidatos:
            if outro.id == ignorar_id or outro.status == STATUS_CANCELADO:
                continue
            if intervalos_se_sobrepoem(inicio, fim, outro.inicio, outro.fim):
                raise Conflito(_mensagem_conflito(barbeiro, outro.inicio, outro.fim))

    def _gravar(self, operacao, agendamento, barbeiro):
        # Lido antes: depois do rollback os objetos da sessao expiram.
        nome_barbeiro = barbeiro.nome
        try:
            return operacao(agendamento)
        except IntegrityError as erro:
            self.repositorio.desfazer()
            if getattr(erro.orig, "pgcode", None) != _VIOLACAO_EXCLUSAO:
                raise
            # Outra requisicao ocupou o horario entre a checagem e o commit.
            raise Conflito(
                f"O horário acabou de ser ocupado na agenda de {nome_barbeiro}. "
                "Escolha outro horário."
            )


def _mensagem_conflito(barbeiro, inicio, fim):
    inicio = inicio.astimezone(FUSO_BARBEARIA)
    fim = fim.astimezone(FUSO_BARBEARIA)
    return (
        f"{barbeiro.nome} já tem agendamento em {inicio:%d/%m/%Y} "
        f"das {inicio:%H:%M} às {fim:%H:%M}. Escolha outro horário."
    )
