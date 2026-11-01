import { http } from './http';

export const authApi = {
  login: (email, senha) => http.post('/auth/login', { email, senha }),
  cadastrar: (dados) => http.post('/auth/register', dados),
  perfil: () => http.get('/auth/me'),
  listarBarbeiros: () => http.get('/auth/barbeiros')
};
