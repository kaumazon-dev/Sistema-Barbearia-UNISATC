import { useApp } from '../state/AppStore';
import AgendamentoForm from '../forms/AgendamentoForm';
import RemarcarForm from '../forms/RemarcarForm';
import ClienteForm from '../forms/ClienteForm';
import ClienteDetalhe from '../forms/ClienteDetalhe';
import ServicoForm from '../forms/ServicoForm';
import ProdutoForm from '../forms/ProdutoForm';
import MovimentacaoForm from '../forms/MovimentacaoForm';
import HistoricoProduto from '../forms/HistoricoProduto';
import Confirmacao from '../forms/Confirmacao';

/**
 * Um unico ponto de renderizacao de modais.
 * Qualquer tela abre qualquer modal com abrirModal('agendamento').
 */
const registro = {
  agendamento: AgendamentoForm,
  remarcar: RemarcarForm,
  cliente: ClienteForm,
  clienteDetalhe: ClienteDetalhe,
  servico: ServicoForm,
  produto: ProdutoForm,
  movimentacao: MovimentacaoForm,
  historicoProduto: HistoricoProduto,
  confirmacao: Confirmacao
};

export default function ModalHost() {
  const { modal } = useApp();
  if (!modal) return null;

  const Componente = registro[modal.tipo];
  if (!Componente) return null;

  // key remonta o formulario ao trocar de registro editado
  return <Componente key={`${modal.tipo}-${modal.dados?.id ?? 'novo'}`} dados={modal.dados} />;
}
