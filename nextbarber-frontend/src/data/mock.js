/**
 * Dados ficticios que alimentam o estado inicial da aplicacao.
 *
 * Este projeto e apenas um modelo de apresentacao: nada aqui vem de API.
 * Valores monetarios ficam como numero; a formatacao acontece na tela
 * (src/utils/formato.js).
 */

export const unidade = {
  nome: 'Unidade Criciúma',
  aberta: true,
  expediente: '08:00 às 20:00',
  dataExtenso: 'Sábado, 14 Out',
  metaDiaria: 3000,
  /** Quantos horarios a unidade comporta no dia inteiro. */
  capacidadeDiaria: 23,
  /**
   * O que ja aconteceu antes do trecho de agenda que a tabela mostra.
   * Serve para os indicadores abrirem com os numeros do modelo do Figma
   * (18 agendamentos, R$ 2.450, 12 atendidos) e ainda assim reagirem
   * quando alguem cria ou conclui um atendimento na apresentacao.
   */
  baseDoDia: {
    agendamentos: 11,
    atendidos: 11,
    faturamento: 2365
  }
};

export const usuario = {
  nome: 'Bruno',
  nomeCompleto: 'Bruno Ferraz',
  papel: 'Administrador',
  iniciais: 'BF'
};

/** Fluxo de status de um agendamento. */
export const STATUS = {
  AGUARDANDO: 'Aguardando',
  CONFIRMADO: 'Confirmado',
  EM_ATENDIMENTO: 'Em Atendimento',
  CONCLUIDO: 'Concluído',
  CANCELADO: 'Cancelado'
};

export const agendamentos = [
  { id: 1, horario: '09:00', clienteId: 1, barbeiroId: 1, servicoId: 2, valor: 85, status: STATUS.CONCLUIDO },
  { id: 2, horario: '09:45', clienteId: 2, barbeiroId: 2, servicoId: 3, valor: 55, status: STATUS.EM_ATENDIMENTO },
  { id: 3, horario: '10:30', clienteId: 3, barbeiroId: 3, servicoId: 1, valor: 50, status: STATUS.EM_ATENDIMENTO },
  { id: 4, horario: '11:15', clienteId: 4, barbeiroId: 4, servicoId: 4, valor: 45, status: STATUS.AGUARDANDO },
  { id: 5, horario: '12:00', clienteId: 5, barbeiroId: 1, servicoId: 5, valor: 120, status: STATUS.CONFIRMADO },
  { id: 6, horario: '13:30', clienteId: 6, barbeiroId: 2, servicoId: 2, valor: 85, status: STATUS.CONFIRMADO },
  { id: 7, horario: '14:15', clienteId: 7, barbeiroId: 3, servicoId: 6, valor: 40, status: STATUS.AGUARDANDO },
  { id: 8, horario: '15:00', clienteId: 8, barbeiroId: 4, servicoId: 7, valor: 65, status: STATUS.CANCELADO }
];

export const barbeiros = [
  { id: 1, apelido: 'Felipe Mago', nomeAgenda: 'Felipe "Mago"', nome: 'Felipe Castro de Souza', iniciais: 'FC', situacao: 'Disponível', especialidade: 'Coloração e platinado', avaliacao: 4.9, comissao: 45 },
  { id: 2, apelido: 'Igor Lima', nomeAgenda: 'Igor Lima', nome: 'Igor Mendes Lima', iniciais: 'IL', situacao: 'Ocupado', especialidade: 'Degradê e navalhado', avaliacao: 4.8, comissao: 40 },
  { id: 3, apelido: 'Carlos Gilete', nomeAgenda: 'Carlos "Gilete"', nome: 'Carlos Eduardo Gilete', iniciais: 'CG', situacao: 'Ocupado', especialidade: 'Barba e navalha', avaliacao: 4.7, comissao: 40 },
  { id: 4, apelido: 'Vitinho', nomeAgenda: 'Vitinho', nome: 'Vitor Gabriel dos Santos', iniciais: 'VS', situacao: 'Intervalo', especialidade: 'Corte clássico', avaliacao: 4.6, comissao: 35 }
];

export const clientes = [
  { id: 1, nome: 'Thiago Silva', iniciais: 'TS', telefone: '(48) 99811-4420', ultimaVisita: '14 Out', visitas: 23, ticket: 85, plano: 'VIP' },
  { id: 2, nome: 'Bruno Henrique', iniciais: 'BH', telefone: '(48) 99640-1187', ultimaVisita: '14 Out', visitas: 11, ticket: 55, plano: 'Recorrente' },
  { id: 3, nome: 'Rodrigo Santos', iniciais: 'RS', telefone: '(48) 99123-7765', ultimaVisita: '02 Out', visitas: 7, ticket: 50, plano: 'Recorrente' },
  { id: 4, nome: 'Matheus Oliveira', iniciais: 'MO', telefone: '(48) 98876-2210', ultimaVisita: '28 Set', visitas: 4, ticket: 45, plano: 'Novo' },
  { id: 5, nome: 'Lucas Almeida', iniciais: 'LA', telefone: '(48) 99502-9934', ultimaVisita: '14 Out', visitas: 31, ticket: 120, plano: 'VIP' },
  { id: 6, nome: 'Guilherme Costa', iniciais: 'GC', telefone: '(48) 99377-6001', ultimaVisita: '10 Out', visitas: 15, ticket: 85, plano: 'Recorrente' },
  { id: 7, nome: 'André Martins', iniciais: 'AM', telefone: '(48) 99044-3128', ultimaVisita: '05 Set', visitas: 2, ticket: 40, plano: 'Novo' },
  { id: 8, nome: 'Pedro Nogueira', iniciais: 'PN', telefone: '(48) 99288-5512', ultimaVisita: '30 Set', visitas: 6, ticket: 65, plano: 'Recorrente' }
];

export const servicos = [
  { id: 1, nome: 'Corte Masculino', duracao: 30, preco: 50, categoria: 'Cabelo', realizados: 128, ativo: true },
  { id: 2, nome: 'Corte + Barba', duracao: 50, preco: 85, categoria: 'Combo', realizados: 96, ativo: true },
  { id: 3, nome: 'Degradê Navalhado', duracao: 40, preco: 55, categoria: 'Cabelo', realizados: 74, ativo: true },
  { id: 4, nome: 'Barba Terapia', duracao: 35, preco: 45, categoria: 'Barba', realizados: 61, ativo: true },
  { id: 5, nome: 'Platinado Global', duracao: 120, preco: 120, categoria: 'Química', realizados: 18, ativo: true },
  { id: 6, nome: 'Corte Infantil', duracao: 25, preco: 40, categoria: 'Cabelo', realizados: 33, ativo: true },
  { id: 7, nome: 'Corte + Sobrancelha', duracao: 40, preco: 65, categoria: 'Combo', realizados: 27, ativo: true },
  { id: 8, nome: 'Hidratação Capilar', duracao: 45, preco: 70, categoria: 'Tratamento', realizados: 9, ativo: false }
];

export const notificacoes = [
  { id: 1, titulo: 'Novo agendamento pelo app', texto: 'Lucas Almeida marcou Platinado Global para 12:00.', quando: 'há 4 min' },
  { id: 2, titulo: 'Cancelamento', texto: 'Pedro Nogueira cancelou o horário das 15:00.', quando: 'há 26 min' },
  { id: 3, titulo: 'Meta do dia', texto: 'Faltam R$ 550 para bater a meta diária.', quando: 'há 1 h' },
  { id: 4, titulo: 'Estoque baixo', texto: 'Pomada modeladora com 3 unidades restantes.', quando: 'há 2 h' }
];

export const faturamentoSemana = [
  { dia: 'Seg', valor: 1280 },
  { dia: 'Ter', valor: 1640 },
  { dia: 'Qua', valor: 1490 },
  { dia: 'Qui', valor: 2010 },
  { dia: 'Sex', valor: 2680 },
  { dia: 'Sáb', valor: 2450 },
  { dia: 'Dom', valor: 640 }
];

export const rankingServicos = [
  { nome: 'Corte + Barba', participacao: 34, receita: 8160 },
  { nome: 'Corte Masculino', participacao: 27, receita: 6400 },
  { nome: 'Degradê Navalhado', participacao: 18, receita: 4070 },
  { nome: 'Barba Terapia', participacao: 13, receita: 2745 },
  { nome: 'Platinado Global', participacao: 8, receita: 2160 }
];
