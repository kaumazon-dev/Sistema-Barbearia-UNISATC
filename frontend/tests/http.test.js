import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { http, ErroApi, quandoPerderSessao } from '../src/js/api/http';
import { salvarSessao, limparSessao } from '../src/js/store/sessao';

const responder = (status, corpo) =>
  vi.fn().mockResolvedValue({ ok: status < 400, status, json: () => Promise.resolve(corpo) });

describe('http.js', () => {
  beforeEach(() => limparSessao());
  afterEach(() => vi.unstubAllGlobals());

  it('injeta o token e monta a URL sem parametros vazios', async () => {
    salvarSessao('abc', { papel: 'admin' });
    const fetch = responder(200, []);
    vi.stubGlobal('fetch', fetch);

    await http.get('/clientes', { busca: '', ativo: true, pagina: 2 });

    const [url, opcoes] = fetch.mock.calls[0];
    expect(url).toBe('/api/v1/clientes?ativo=true&pagina=2');
    expect(opcoes.headers.Authorization).toBe('Bearer abc');
  });

  it('erro da API vira ErroApi com codigo e campos', async () => {
    vi.stubGlobal(
      'fetch',
      responder(409, { erro: { codigo: 'CONFLITO', mensagem: 'Horário ocupado.' } })
    );

    const erro = await http.post('/agendamentos', {}).catch((e) => e);
    expect(erro).toBeInstanceOf(ErroApi);
    expect(erro.codigo).toBe('CONFLITO');
    expect(erro.message).toBe('Horário ocupado.');
  });

  it('401 com token avisa que a sessao expirou', async () => {
    salvarSessao('vencido', { papel: 'admin' });
    const aoPerder = vi.fn();
    quandoPerderSessao(aoPerder);
    vi.stubGlobal('fetch', responder(401, { erro: { codigo: 'NAO_AUTENTICADO', mensagem: 'x' } }));

    await http.get('/auth/me').catch(() => {});
    expect(aoPerder).toHaveBeenCalledOnce();
  });

  it('401 sem token (senha errada no login) nao derruba sessao', async () => {
    const aoPerder = vi.fn();
    quandoPerderSessao(aoPerder);
    vi.stubGlobal('fetch', responder(401, { erro: { codigo: 'NAO_AUTENTICADO', mensagem: 'x' } }));

    await http.post('/auth/login', {}).catch(() => {});
    expect(aoPerder).not.toHaveBeenCalled();
  });

  it('servidor fora do ar vira mensagem legivel', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));

    const erro = await http.get('/servicos').catch((e) => e);
    expect(erro.codigo).toBe('SEM_CONEXAO');
  });
});
