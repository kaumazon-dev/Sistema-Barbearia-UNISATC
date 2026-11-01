/**
 * Monta o menu de acoes de um agendamento a partir do status e do papel.
 * Usado no dashboard, na agenda e na ficha do cliente.
 *
 * Segue a maquina de estados da API: so "agendado" muda; concluido e
 * cancelado sao finais.
 */
export function acoesDoAgendamento(item, app) {
  const { usuario, abrirModal, concluirAgendamento, cancelarAgendamento } = app;
  if (item.status !== 'agendado') return [];

  const itens = [];

  if (usuario.papel !== 'cliente') {
    itens.push({
      chave: 'concluir',
      rotulo: 'Concluir atendimento',
      aoClicar: () => concluirAgendamento(item)
    });
  }

  itens.push({
    chave: 'remarcar',
    rotulo: 'Remarcar',
    aoClicar: () => abrirModal('remarcar', item)
  });

  itens.push(
    { chave: 'sep-1', separador: true },
    {
      chave: 'cancelar',
      rotulo: 'Cancelar horário',
      perigo: true,
      aoClicar: () =>
        abrirModal('confirmacao', {
          titulo: 'Cancelar horário',
          texto: `O horário de ${item.cliente.nome} com ${item.barbeiro.nome} será cancelado e liberado na agenda. O registro continua no histórico.`,
          rotuloConfirmar: 'Cancelar horário',
          aoConfirmar: () => cancelarAgendamento(item)
        })
    }
  );

  return itens;
}
