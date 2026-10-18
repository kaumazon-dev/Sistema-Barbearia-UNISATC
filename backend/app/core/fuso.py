"""Fuso horario unico do sistema.

Regra: datetime naive nao entra no sistema. O banco grava timestamptz (UTC por
dentro), a API so aceita data/hora com fuso explicito e responde no fuso da
barbearia. Misturar naive e aware e fonte classica de bug de agenda.
"""

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

FUSO_BARBEARIA = ZoneInfo("America/Sao_Paulo")


def agora():
    return datetime.now(timezone.utc)


def intervalo_do_dia(dia):
    """[00:00 do dia, 00:00 do dia seguinte) no fuso da barbearia."""
    inicio = datetime.combine(dia, time.min, tzinfo=FUSO_BARBEARIA)
    # Soma no calendario e nao 24h: dia de troca de horario nao tem 24h.
    fim = datetime.combine(dia + timedelta(days=1), time.min, tzinfo=FUSO_BARBEARIA)
    return inicio, fim
