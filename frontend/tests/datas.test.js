import { describe, expect, it } from 'vitest';
import { diaISO, hora, montarInicio, separarInicio, somarDias, rotuloPeriodo } from '../src/js/utils/datas';

describe('datas no fuso da barbearia', () => {
  it('o inicio enviado leva o fuso de Brasilia, como a API exige', () => {
    expect(montarInicio('2026-11-03', '09:00')).toBe('2026-11-03T09:00:00-03:00');
  });

  it('horario da API e exibido em Brasilia mesmo vindo em UTC', () => {
    expect(hora('2026-11-03T12:00:00Z')).toBe('09:00');
  });

  it('23h de Brasilia ainda e o mesmo dia, mesmo ja sendo amanha em UTC', () => {
    expect(diaISO(new Date('2026-11-04T02:00:00Z'))).toBe('2026-11-03');
  });

  it('separar e montar de novo devolve o mesmo horario (remarcacao)', () => {
    const { dia, horario } = separarInicio('2026-11-03T14:30:00-03:00');
    expect(montarInicio(dia, horario)).toBe('2026-11-03T14:30:00-03:00');
  });

  it('somar dias atravessa mes e ano', () => {
    expect(somarDias('2026-10-31', 1)).toBe('2026-11-01');
    expect(somarDias('2026-12-31', 1)).toBe('2027-01-01');
    expect(somarDias('2026-03-01', -1)).toBe('2026-02-28');
  });

  it('rotulo de semana mostra a segunda-feira', () => {
    expect(rotuloPeriodo('2026-10-05', 'semana')).toBe('05/10');
  });
});
