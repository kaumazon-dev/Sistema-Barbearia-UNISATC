import { STATUS } from '../data/mock';

/**
 * Monta o menu de acoes de um agendamento a partir do status atual.
 * Usado tanto no dashboard quanto na tela de Agendamentos.
 */
export function acoesDoAgendamento(item, app) {
  const { mudarStatus, removerAgendamento, abrirModal } = app;
  const itens = [];

  if (item.status === STATUS.AGUARDANDO) {
    itens.push({
      chave: 'confirmar',
      rotulo: 'Confirmar',
      aoClicar: () => mudarStatus(item.id, STATUS.CONFIRMADO)
    });
  }

  if (item.status === STATUS.AGUARDANDO || item.status === STATUS.CONFIRMADO) {
    itens.push({
      chave: 'iniciar',
      rotulo: 'Iniciar atendimento',
      aoClicar: () => mudarStatus(item.id, STATUS.EM_ATENDIMENTO)
    });
  }

  if (item.status === STATUS.EM_ATENDIMENTO) {
    itens.push({
      chave: 'concluir',
      rotulo: 'Concluir atendimento',
      aoClicar: () => mudarStatus(item.id, STATUS.CONCLUIDO)
    });
  }

  if (item.status === STATUS.CANCELADO || item.status === STATUS.CONCLUIDO) {
    itens.push({
      chave: 'reabrir',
      rotulo: 'Reabrir',
      aoClicar: () => mudarStatus(item.id, STATUS.AGUARDANDO)
    });
  }

  itens.push(
    { chave: 'sep-1', separador: true },
    {
      chave: 'editar',
      rotulo: 'Editar agendamento',
      aoClicar: () => abrirModal('agendamento', item)
    }
  );

  if (item.status !== STATUS.CANCELADO) {
    itens.push({
      chave: 'cancelar',
      rotulo: 'Cancelar horário',
      aoClicar: () => mudarStatus(item.id, STATUS.CANCELADO)
    });
  }

  itens.push({
    chave: 'excluir',
    rotulo: 'Excluir',
    perigo: true,
    aoClicar: () =>
      abrirModal('confirmacao', {
        titulo: 'Excluir agendamento',
        texto: `O horário das ${item.horario} de ${item.cliente} será removido da agenda.`,
        aoConfirmar: () => removerAgendamento(item.id)
      })
  });

  return itens;
}
