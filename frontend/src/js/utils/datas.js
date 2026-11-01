/**
 * Datas sempre no fuso da barbearia, como a API (America/Sao_Paulo).
 *
 * Assim a agenda mostra o mesmo horario em qualquer computador, mesmo que o
 * navegador esteja em outro fuso.
 */

const FUSO = 'America/Sao_Paulo';
// Brasilia nao tem horario de verao desde 2019: o offset e fixo.
const OFFSET = '-03:00';

const partes = (data, opcoes) =>
  new Intl.DateTimeFormat('pt-BR', { timeZone: FUSO, ...opcoes }).format(data);

/** Hoje em AAAA-MM-DD, no fuso da barbearia. */
export function hojeISO() {
  return diaISO(new Date());
}

/** Date -> AAAA-MM-DD no fuso da barbearia. */
export function diaISO(data) {
  // en-CA formata como AAAA-MM-DD
  return new Intl.DateTimeFormat('en-CA', { timeZone: FUSO }).format(data);
}

/** Soma dias a uma data AAAA-MM-DD. */
export function somarDias(dia, quantidade) {
  const data = new Date(`${dia}T12:00:00${OFFSET}`);
  data.setUTCDate(data.getUTCDate() + quantidade);
  return diaISO(data);
}

/** Primeiro dia do mes de uma data AAAA-MM-DD. */
export function inicioDoMes(dia) {
  return `${dia.slice(0, 8)}01`;
}

/** "2026-10-20T14:30:00-03:00" -> "14:30". */
export function hora(iso) {
  return partes(new Date(iso), { hour: '2-digit', minute: '2-digit' });
}

/** "2026-10-20T14:30:00-03:00" -> "20/10/2026". */
export function data(iso) {
  return partes(new Date(iso), { day: '2-digit', month: '2-digit', year: 'numeric' });
}

/** "2026-10-20" -> "20/10/2026". */
export function dataDoDia(dia) {
  const [a, m, d] = dia.split('-');
  return `${d}/${m}/${a}`;
}

/** "2026-10-20" -> "terça-feira, 20 de outubro". */
export function diaPorExtenso(dia) {
  return partes(new Date(`${dia}T12:00:00${OFFSET}`), {
    weekday: 'long',
    day: 'numeric',
    month: 'long'
  });
}

/** Partes do formulario (AAAA-MM-DD + HH:MM) -> ISO com fuso, como a API exige. */
export function montarInicio(dia, horario) {
  return `${dia}T${horario}:00${OFFSET}`;
}

/** ISO -> { dia, horario } para preencher o formulario de remarcacao. */
export function separarInicio(iso) {
  const quando = new Date(iso);
  return { dia: diaISO(quando), horario: hora(iso) };
}

/** Rotulo de semana ("2026-10-05") ou mes ("2026-10") do dashboard. */
export function rotuloPeriodo(rotulo, granularidade) {
  if (granularidade === 'mes') {
    const [a, m] = rotulo.split('-');
    return partes(new Date(`${a}-${m}-15T12:00:00${OFFSET}`), { month: 'short', year: '2-digit' });
  }
  return dataDoDia(rotulo).slice(0, 5);
}
