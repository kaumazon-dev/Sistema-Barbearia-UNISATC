const tons = {
  Confirmado: 'green',
  'Em Atendimento': 'blue',
  Concluído: 'roxo',
  Aguardando: 'amber',
  Cancelado: 'red',
  Disponível: 'green',
  Ocupado: 'amber',
  Intervalo: 'neutral',
  Ativo: 'green',
  Inativo: 'neutral',
  VIP: 'amber',
  Recorrente: 'blue',
  Novo: 'neutral'
};

export default function StatusBadge({ status }) {
  return <span className={`badge badge--${tons[status] || 'neutral'}`}>{status}</span>;
}
