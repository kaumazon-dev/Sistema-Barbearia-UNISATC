import { afterEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import MenuAcoes from '../src/js/components/MenuAcoes';

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

let raiz;
let container;

function montar(itens, retanguloDoBotao) {
  container = document.createElement('div');
  // Simula a tabela que corta o que passa da borda.
  container.style.overflow = 'auto';
  document.body.appendChild(container);
  raiz = createRoot(container);
  act(() => raiz.render(<MenuAcoes itens={itens} />));
  const botao = container.querySelector('.menu-acoes');
  botao.getBoundingClientRect = () => retanguloDoBotao;
  return container.querySelector('button');
}

afterEach(() => {
  act(() => raiz.unmount());
  container.remove();
});

const itens = [
  { chave: 'remarcar', rotulo: 'Remarcar', aoClicar: vi.fn() },
  { chave: 'cancelar', rotulo: 'Cancelar horário', aoClicar: vi.fn() }
];

describe('MenuAcoes', () => {
  it('abre fora da tabela, para nao ser cortado pelo overflow', () => {
    const botao = montar(itens, { top: 100, bottom: 128, right: 900 });

    act(() => botao.click());

    const lista = document.querySelector('.menu-acoes__lista');
    expect(lista).not.toBeNull();
    expect(container.contains(lista)).toBe(false);
    expect(lista.style.top).toBe('134px');
  });

  it('sem espaco embaixo, abre para cima', () => {
    const fundo = window.innerHeight;
    const botao = montar(itens, { top: fundo - 40, bottom: fundo - 12, right: 900 });

    act(() => botao.click());

    const lista = document.querySelector('.menu-acoes__lista');
    expect(lista.style.top).toBe('');
    expect(lista.style.bottom).toBe('46px');
  });

  it('clicar num item executa a acao e fecha o menu', () => {
    const botao = montar(itens, { top: 100, bottom: 128, right: 900 });
    act(() => botao.click());

    act(() => document.querySelector('[role="menuitem"]').click());

    expect(itens[0].aoClicar).toHaveBeenCalledOnce();
    expect(document.querySelector('.menu-acoes__lista')).toBeNull();
  });
});
