import { http } from './http';

export const produtosApi = {
  listar: ({ ativo } = {}) => http.get('/produtos', { ativo }),
  emFalta: () => http.get('/produtos/em-falta'),
  criar: (dados) => http.post('/produtos', dados),
  atualizar: (id, dados) => http.put(`/produtos/${id}`, dados),
  desativar: (id) => http.delete(`/produtos/${id}`),
  entrada: (id, dados) => http.post(`/produtos/${id}/entradas`, dados),
  saida: (id, dados) => http.post(`/produtos/${id}/saidas`, dados),
  movimentacoes: (id, { tipo, pagina, porPagina } = {}) =>
    http.get(`/produtos/${id}/movimentacoes`, { tipo, pagina, por_pagina: porPagina })
};
