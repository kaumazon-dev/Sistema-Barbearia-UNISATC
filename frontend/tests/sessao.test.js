import { describe, expect, it } from 'vitest';
import { podeAcessar, telaInicial } from '../src/js/store/sessao';

describe('telas por papel', () => {
  it('cada papel abre na sua tela inicial', () => {
    expect(telaInicial('admin')).toBe('dashboard');
    expect(telaInicial('barbeiro')).toBe('agendamentos');
    expect(telaInicial('cliente')).toBe('agendamentos');
  });

  it('estoque, dashboard e relatorios sao so do admin', () => {
    for (const tela of ['estoque', 'dashboard', 'relatorios']) {
      expect(podeAcessar('admin', tela)).toBe(true);
      expect(podeAcessar('barbeiro', tela)).toBe(false);
      expect(podeAcessar('cliente', tela)).toBe(false);
    }
  });

  it('cliente nao ve a lista de clientes nem a equipe', () => {
    expect(podeAcessar('cliente', 'clientes')).toBe(false);
    expect(podeAcessar('cliente', 'barbeiros')).toBe(false);
  });

  it('papel desconhecido nao acessa nada', () => {
    expect(podeAcessar('hacker', 'agendamentos')).toBe(false);
  });
});
