import { http } from './http';

export const authApi = {
  login: (email, senha) => http.post('/auth/login', { email, senha }),
  cadastrar: (dados) => http.post('/auth/register', dados),
  esqueciSenha: (email) => http.post('/auth/esqueci-senha', { email }),
  redefinirSenha: (token, senha) => http.post('/auth/redefinir-senha', { token, senha }),
  perfil: () => http.get('/auth/me'),
  listarBarbeiros: () => http.get('/auth/barbeiros'),
  listarUsuarios: (papel) => http.get('/auth/usuarios', { papel }),
  alterarPapel: (id, papel) => http.patch(`/auth/usuarios/${id}/papel`, { papel })
};
