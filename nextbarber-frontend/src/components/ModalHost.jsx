import { useApp } from '../state/AppStore';
import AgendamentoForm from '../forms/AgendamentoForm';
import ClienteForm from '../forms/ClienteForm';
import ClienteDetalhe from '../forms/ClienteDetalhe';
import BarbeiroForm from '../forms/BarbeiroForm';
import ServicoForm from '../forms/ServicoForm';
import Confirmacao from '../forms/Confirmacao';

/**
 * Um unico ponto de renderizacao de modais.
 * Qualquer tela abre qualquer modal com abrirModal('agendamento').
 */
const registro = {
  agendamento: AgendamentoForm,
  cliente: ClienteForm,
  clienteDetalhe: ClienteDetalhe,
  barbeiro: BarbeiroForm,
  servico: ServicoForm,
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
