"""Avisos por e-mail quando um agendamento e criado.

O cliente recebe a confirmacao e o barbeiro fica sabendo do horario novo na
agenda dele. Usa o mesmo enviador do "esqueci minha senha": sem MAIL_SERVIDOR,
o e-mail vai para o log.

Avisar e consequencia de agendar, nao parte dele: se o envio falhar, o
agendamento ja esta gravado e a requisicao nao pode responder erro.
"""

import logging

from app.core.fuso import FUSO_BARBEARIA

logger = logging.getLogger(__name__)

ASSUNTO_CLIENTE = "NextBarber - agendamento confirmado"
ASSUNTO_BARBEIRO = "NextBarber - novo agendamento na sua agenda"


class NotificadorAgendamento:
    def __init__(self, enviador_email):
        self.enviador_email = enviador_email

    def agendamento_criado(self, agendamento):
        detalhes = _detalhes(agendamento)
        cliente = agendamento.cliente
        barbeiro = agendamento.barbeiro

        self._enviar(
            cliente.email,
            ASSUNTO_CLIENTE,
            f"Olá, {cliente.nome}!\n\n"
            f"Seu horário com {barbeiro.nome} está marcado.\n\n"
            f"{detalhes}\n\n"
            "Se não puder comparecer, cancele ou remarque pelo NextBarber.",
        )
        self._enviar(
            barbeiro.email,
            ASSUNTO_BARBEIRO,
            f"Olá, {barbeiro.nome}!\n\n"
            f"{cliente.nome} marcou um horário com você.\n\n"
            f"{detalhes}",
        )

    def _enviar(self, para, assunto, corpo):
        try:
            self.enviador_email.enviar(para, assunto, corpo)
        except Exception:
            logger.exception("Falha ao notificar %s sobre agendamento", para)


def _detalhes(agendamento):
    inicio = agendamento.inicio.astimezone(FUSO_BARBEARIA)
    fim = agendamento.fim.astimezone(FUSO_BARBEARIA)
    servicos = ", ".join(item.servico.nome for item in agendamento.itens)
    total = sum(item.preco_cobrado for item in agendamento.itens)
    linhas = [
        f"Data: {inicio:%d/%m/%Y}",
        f"Horário: {inicio:%H:%M} às {fim:%H:%M}",
        f"Serviços: {servicos}",
        f"Total: R$ {total:.2f}".replace(".", ","),
    ]
    if agendamento.observacao:
        linhas.append(f"Observação: {agendamento.observacao}")
    return "\n".join(linhas)
