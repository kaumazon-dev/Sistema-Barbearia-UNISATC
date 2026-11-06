import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot } from 'react-dom/client';

vi.mock('../src/js/store/AppStore', () => ({
  useApp: () => ({ entrar: vi.fn(), cadastrar: vi.fn() })
}));

const esqueciSenha = vi.fn();
const redefinirSenha = vi.fn();
vi.mock('../src/js/api/auth.api', () => ({
  authApi: {
    esqueciSenha: (...args) => esqueciSenha(...args),
    redefinirSenha: (...args) => redefinirSenha(...args)
  }
}));

import Login from '../src/pages/login/Login';

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

let raiz;
let container;

function montar() {
  container = document.createElement('div');
  document.body.appendChild(container);
  raiz = createRoot(container);
  act(() => raiz.render(<Login />));
}

function digitar(seletor, valor) {
  const campo = container.querySelector(seletor);
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  act(() => {
    setter.call(campo, valor);
    campo.dispatchEvent(new Event('input', { bubbles: true }));
  });
}

function botaoComTexto(texto) {
  return [...container.querySelectorAll('button')].find((b) => b.textContent === texto);
}

async function enviarFormulario() {
  await act(async () => {
    container.querySelector('form').dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
  });
}

beforeEach(() => {
  esqueciSenha.mockReset();
  redefinirSenha.mockReset();
});

afterEach(() => {
  act(() => raiz.unmount());
  container.remove();
  window.history.replaceState(null, '', '/');
});

describe('Esqueci minha senha', () => {
  it('pede o link pelo e-mail e mostra a mensagem da API', async () => {
    esqueciSenha.mockResolvedValue({ mensagem: 'Se o e-mail estiver cadastrado...' });
    montar();

    act(() => botaoComTexto('Esqueci minha senha').click());
    expect(container.querySelector('#lg-senha')).toBeNull();

    digitar('#lg-email', 'ana@exemplo.com');
    await enviarFormulario();

    expect(esqueciSenha).toHaveBeenCalledWith('ana@exemplo.com');
    expect(container.querySelector('[role="status"]').textContent).toContain('Se o e-mail');
  });

  it('abre em "nova senha" quando a URL traz o token e limpa a URL ao salvar', async () => {
    window.history.replaceState(null, '', '/?redefinir=tok123');
    redefinirSenha.mockResolvedValue({ mensagem: 'Senha redefinida.' });
    montar();

    expect(container.querySelector('h1').textContent).toBe('Nova senha');
    digitar('#lg-senha', 'senha-nova-123');
    digitar('#lg-confirmacao', 'senha-nova-123');
    await enviarFormulario();

    expect(redefinirSenha).toHaveBeenCalledWith('tok123', 'senha-nova-123');
    expect(window.location.search).toBe('');
    expect(container.querySelector('h1').textContent).toBe('Entrar');
  });

  it('nao envia se a confirmacao nao confere', async () => {
    window.history.replaceState(null, '', '/?redefinir=tok123');
    montar();

    digitar('#lg-senha', 'senha-nova-123');
    digitar('#lg-confirmacao', 'outra-coisa-99');
    await enviarFormulario();

    expect(redefinirSenha).not.toHaveBeenCalled();
    expect(container.textContent).toContain('As senhas não conferem.');
  });
});
