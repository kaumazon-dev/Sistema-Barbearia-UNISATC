import { http } from './http';

export const agendamentosApi = {
  /** Paginado. dia em AAAA-MM-DD (dia de Brasilia). */
  listar: ({ dia, barbeiroId, clienteId, status, pagina, porPagina } = {}) =>
    http.get('/agendamentos', {
      dia,
      barbeiro_id: barbeiroId,
      cliente_id: clienteId,
      status,
      pagina,
      por_pagina: porPagina
    }),
  criar: (dados) => http.post('/agendamentos', dados),
  remarcar: (id, dados) => http.patch(`/agendamentos/${id}`, dados),
  cancelar: (id) => http.post(`/agendamentos/${id}/cancelar`),
  concluir: (id) => http.post(`/agendamentos/${id}/concluir`)
};
