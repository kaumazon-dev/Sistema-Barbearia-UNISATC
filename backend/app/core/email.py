"""Envio de e-mail da aplicacao.

Duas implementacoes com o mesmo metodo enviar(para, assunto, corpo):

- EnviadorEmailSmtp: envia de verdade, quando MAIL_SERVIDOR esta configurado.
- EnviadorEmailLog: so escreve no log. E o padrao em dev e nos testes, para o
  sistema funcionar sem conta de e-mail (o link aparece no terminal do Flask).

O service recebe o enviador pronto e nao sabe qual dos dois e: trocar SMTP por
outro provedor (SendGrid, Resend...) e escrever outra classe com enviar().
"""

import logging
import smtplib
import threading
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class EnviadorEmailLog:
    def __init__(self):
        self.enviados = []

    def enviar(self, para, assunto, corpo):
        self.enviados.append({"para": para, "assunto": assunto, "corpo": corpo})
        logger.warning(
            "E-mail NAO enviado (MAIL_SERVIDOR nao configurado).\n"
            "Para: %s\nAssunto: %s\n\n%s",
            para,
            assunto,
            corpo,
        )


class EnviadorEmailSmtp:
    def __init__(self, servidor, porta, usuario, senha, remetente, usar_tls=True):
        self.servidor = servidor
        self.porta = porta
        self.usuario = usuario
        self.senha = senha
        self.remetente = remetente
        self.usar_tls = usar_tls

    def enviar(self, para, assunto, corpo):
        mensagem = EmailMessage()
        mensagem["From"] = self.remetente
        mensagem["To"] = para
        mensagem["Subject"] = assunto
        mensagem.set_content(corpo)

        # Em outra thread: falar com o SMTP leva segundos. Se a resposta da API
        # esperasse, "e-mail cadastrado" demoraria mais que "nao cadastrado" e o
        # tempo de resposta revelaria quem tem conta.
        threading.Thread(target=self._enviar_agora, args=(mensagem,), daemon=True).start()

    def _enviar_agora(self, mensagem):
        try:
            with smtplib.SMTP(self.servidor, self.porta, timeout=15) as smtp:
                if self.usar_tls:
                    smtp.starttls()
                if self.usuario:
                    smtp.login(self.usuario, self.senha)
                smtp.send_message(mensagem)
        except Exception:
            logger.exception("Falha ao enviar e-mail para %s", mensagem["To"])


def criar_enviador_email(config):
    if not config.get("MAIL_SERVIDOR"):
        return EnviadorEmailLog()
    return EnviadorEmailSmtp(
        servidor=config["MAIL_SERVIDOR"],
        porta=config["MAIL_PORTA"],
        usuario=config.get("MAIL_USUARIO"),
        senha=config.get("MAIL_SENHA"),
        remetente=config.get("MAIL_REMETENTE") or config.get("MAIL_USUARIO"),
        usar_tls=config["MAIL_USAR_TLS"],
    )
