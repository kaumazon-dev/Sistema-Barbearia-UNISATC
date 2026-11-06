import { http } from './http';

export const servicosApi = {
  listar: ({ ativo } = {}) => http.get('/servicos', { ativo }),
  criar: (dados) => http.post('/servicos', dados),
  atualizar: (id, dados) => http.put(`/servicos/${id}`, dados),
  desativar: (id) => http.delete(`/servicos/${id}`)
};
