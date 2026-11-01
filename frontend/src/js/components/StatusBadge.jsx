const tons = {
  Agendado: 'blue',
  Concluído: 'green',
  Cancelado: 'red',
  Disponível: 'green',
  Ocupado: 'amber',
  Livre: 'neutral',
  Ativo: 'green',
  Inativo: 'neutral',
  'Em falta': 'red',
  'Em dia': 'green',
  Entrada: 'green',
  Saída: 'amber'
};

export default function StatusBadge({ status }) {
  return <span className={`badge badge--${tons[status] || 'neutral'}`}>{status}</span>;
}
