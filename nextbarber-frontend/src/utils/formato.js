/** Formatacao de valores exibidos na interface. */

export const formatarBRL = (valor) =>
  Number(valor || 0).toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: Number.isInteger(Number(valor)) ? 0 : 2
  });

export const iniciaisDe = (nome) =>
  String(nome || '')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((parte) => parte[0] || '')
    .join('')
    .toUpperCase() || '??';

export const minutosParaTexto = (min) => `${min} min`;

/** "09:00" -> 540, usado so para ordenar a agenda. */
export const horarioEmMinutos = (horario) => {
  const [h, m] = String(horario).split(':').map(Number);
  return (h || 0) * 60 + (m || 0);
};
