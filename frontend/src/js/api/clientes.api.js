import { http } from './http';

export const clientesApi = {
  /** Paginado: { itens, pagina, por_pagina, total, paginas }. */
  listar: ({ busca, ativo, pagina, porPagina } = {}) =>
    http.get('/clientes', { busca, ativo, pagina, por_pagina: porPagina }),
  buscar: (id) => http.get(`/clientes/${id}`),
  criar: (dados) => http.post('/clientes', dados),
  atualizar: (id, dados) => http.put(`/clientes/${id}`, dados),
  desativar: (id) => http.delete(`/clientes/${id}`)
};
