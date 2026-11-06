import { describe, expect, it } from 'vitest';
import { formatarBRL, formatarQuantidade, iniciaisDe, somarDinheiro } from '../src/js/utils/formato';

describe('somarDinheiro', () => {
  it('soma strings da API sem erro de centavo do float', () => {
    // 0.1 + 0.2 em float da 0.30000000000000004
    expect(somarDinheiro(['0.10', '0.20'])).toBe(0.3);
    expect(somarDinheiro(['35.90', '25.50', '19.99'])).toBe(81.39);
  });

  it('lista vazia e valores nulos contam como zero', () => {
    expect(somarDinheiro([])).toBe(0);
    expect(somarDinheiro([null, '10.00'])).toBe(10);
  });
});

describe('formatacao', () => {
  it('moeda em real com duas casas', () => {
    expect(formatarBRL('35.9').replace(/\s/g, ' ')).toBe('R$ 35,90');
  });

  it('quantidade sem zeros sobrando', () => {
    expect(formatarQuantidade('10.50')).toBe('10,5');
    expect(formatarQuantidade('3.00')).toBe('3');
  });

  it('iniciais do nome', () => {
    expect(iniciaisDe('joão da silva')).toBe('JD');
    expect(iniciaisDe('')).toBe('??');
  });
});
