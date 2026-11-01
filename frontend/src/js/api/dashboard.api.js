import { http } from './http';

/** Todas aceitam de/ate (AAAA-MM-DD). Sem os dois, a API usa o mes atual. */
export const dashboardApi = {
  atendimentos: ({ de, ate, granularidade } = {}) =>
    http.get('/dashboard/atendimentos', { de, ate, granularidade }),
  faturamento: ({ de, ate, granularidade } = {}) =>
    http.get('/dashboard/faturamento', { de, ate, granularidade }),
  ranking: ({ de, ate, limite } = {}) => http.get('/dashboard/servicos-ranking', { de, ate, limite }),
  cancelamento: ({ de, ate } = {}) => http.get('/dashboard/cancelamento', { de, ate })
};
