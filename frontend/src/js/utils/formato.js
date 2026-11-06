/** Formatacao de valores exibidos na interface. */

/**
 * A API manda dinheiro como string ("35.90"). Number() aqui e so para exibir;
 * soma de dinheiro usa somarDinheiro, em centavos inteiros.
 */
export const formatarBRL = (valor) =>
  Number(valor || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

/** Soma strings monetarias sem erro de centavo do float. */
export const somarDinheiro = (valores) =>
  valores.reduce((centavos, v) => centavos + Math.round(Number(v || 0) * 100), 0) / 100;

/** "10.50" -> "10,5"; quantidade de estoque sem zeros sobrando. */
export const formatarQuantidade = (valor) =>
  Number(valor || 0).toLocaleString('pt-BR', { maximumFractionDigits: 2 });

export const iniciaisDe = (nome) =>
  String(nome || '')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte[0] || '')
    .join('')
    .toUpperCase() || '??';

/** Rotulo e cor de cada status do agendamento (valores da API). */
export const STATUS = {
  agendado: 'Agendado',
  concluido: 'Concluído',
  cancelado: 'Cancelado'
};
