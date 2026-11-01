/**
 * Unico ponto do front que conhece a URL da API e o cabecalho de autorizacao.
 *
 * Nenhuma tela chama fetch direto: todas passam pelos modulos *.api.js, que
 * passam por aqui. No deploy, so a variavel VITE_API_URL muda.
 */
import { lerToken } from '../store/sessao';

// Local (Vite ou nginx do compose) a API responde na mesma origem, via proxy.
const URL_BASE = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '');

/** Erro no formato do contrato: { erro: { codigo, mensagem, campos? } }. */
export class ErroApi extends Error {
  constructor(status, codigo, mensagem, campos = null) {
    super(mensagem);
    this.status = status;
    this.codigo = codigo;
    this.campos = campos;
  }
}

let aoPerderSessao = () => {};

/** O AppStore registra aqui o que fazer quando o token expira (401). */
export function quandoPerderSessao(callback) {
  aoPerderSessao = callback;
}

function montarUrl(caminho, parametros) {
  const url = `${URL_BASE}${caminho}`;
  if (!parametros) return url;

  // Parametro vazio fica de fora: a API trata ausente e vazio igual, mas
  // assim a URL sai limpa.
  const busca = new URLSearchParams();
  Object.entries(parametros).forEach(([chave, valor]) => {
    if (valor !== undefined && valor !== null && valor !== '') busca.append(chave, valor);
  });
  const texto = busca.toString();
  return texto ? `${url}?${texto}` : url;
}

async function requisitar(metodo, caminho, { corpo, parametros } = {}) {
  const cabecalhos = { Accept: 'application/json' };
  const token = lerToken();
  if (token) cabecalhos.Authorization = `Bearer ${token}`;
  if (corpo !== undefined) cabecalhos['Content-Type'] = 'application/json';

  let resposta;
  try {
    resposta = await fetch(montarUrl(caminho, parametros), {
      method: metodo,
      headers: cabecalhos,
      body: corpo === undefined ? undefined : JSON.stringify(corpo)
    });
  } catch {
    throw new ErroApi(0, 'SEM_CONEXAO', 'Não foi possível falar com o servidor. Verifique a conexão.');
  }

  if (resposta.status === 204) return null;

  const dados = await resposta.json().catch(() => null);

  if (!resposta.ok) {
    const erro = dados?.erro || {};
    // 401 com token em maos = sessao expirada. No login (sem token) o 401 e
    // so senha errada e vai para a tela tratar.
    if (resposta.status === 401 && token) aoPerderSessao();
    throw new ErroApi(
      resposta.status,
      erro.codigo || 'ERRO_INTERNO',
      erro.mensagem || 'Erro inesperado no servidor.',
      erro.campos || null
    );
  }

  return dados;
}

export const http = {
  get: (caminho, parametros) => requisitar('GET', caminho, { parametros }),
  post: (caminho, corpo) => requisitar('POST', caminho, { corpo }),
  put: (caminho, corpo) => requisitar('PUT', caminho, { corpo }),
  patch: (caminho, corpo) => requisitar('PATCH', caminho, { corpo }),
  delete: (caminho) => requisitar('DELETE', caminho)
};
