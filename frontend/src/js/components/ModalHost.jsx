import { useApp } from '../store/AppStore';
import AgendamentoForm from '../../pages/agenda/AgendamentoForm';
import RemarcarForm from '../../pages/agenda/RemarcarForm';
import ClienteForm from '../../pages/clientes/ClienteForm';
import ClienteDetalhe from '../../pages/clientes/ClienteDetalhe';
import ServicoForm from '../../pages/servicos/ServicoForm';
import ProdutoForm from '../../pages/estoque/ProdutoForm';
import MovimentacaoForm from '../../pages/estoque/MovimentacaoForm';
import HistoricoProduto from '../../pages/estoque/HistoricoProduto';
import Confirmacao from './Confirmacao';

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
