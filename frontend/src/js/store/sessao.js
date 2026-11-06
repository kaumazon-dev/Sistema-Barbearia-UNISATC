/**
 * Sessao do usuario logado: token JWT e dados basicos, no localStorage.
 *
 * O papel guardado aqui so decide o que a interface mostra. Quem garante a
 * permissao e o backend: mexer no localStorage nao abre rota protegida.
 */

const CHAVE = 'nextbarber.sessao';

function ler() {
  try {
    return JSON.parse(localStorage.getItem(CHAVE)) || null;
  } catch {
    return null;
  }
}

export function lerSessao() {
  return ler();
}

export function lerToken() {
  return ler()?.token || null;
}

export function salvarSessao(token, usuario) {
  try {
    localStorage.setItem(CHAVE, JSON.stringify({ token, usuario }));
  } catch {
    // Navegador sem storage: a sessao vale ate recarregar a pagina.
  }
}

export function limparSessao() {
  try {
    localStorage.removeItem(CHAVE);
  } catch {
    // nada a limpar
  }
}

/** Telas liberadas por papel. A primeira e a tela inicial do papel. */
export const TELAS_POR_PAPEL = {
  admin: ['dashboard', 'agendamentos', 'clientes', 'barbeiros', 'usuarios', 'servicos', 'estoque', 'relatorios', 'configuracoes'],
  barbeiro: ['agendamentos', 'clientes', 'barbeiros', 'servicos', 'configuracoes'],
  cliente: ['agendamentos', 'servicos', 'configuracoes']
};

export function podeAcessar(papel, tela) {
  return (TELAS_POR_PAPEL[papel] || []).includes(tela);
}

export function telaInicial(papel) {
  return (TELAS_POR_PAPEL[papel] || ['configuracoes'])[0];
}
