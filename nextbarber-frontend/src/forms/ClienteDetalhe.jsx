import Modal from '../components/Modal';
import Avatar from '../components/Avatar';
import StatusBadge from '../components/StatusBadge';
import { useApp } from '../state/AppStore';
import { formatarBRL } from '../utils/formato';

/** Ficha do cliente com o historico vindo da propria agenda. */
export default function ClienteDetalhe({ dados }) {
  const { agendamentos, fecharModal, abrirModal } = useApp();
  const historico = agendamentos.filter((a) => a.clienteId === dados.id);

  return (
    <Modal
      titulo={dados.nome}
      descricao={`${dados.telefone} · ${dados.visitas} visitas`}
      largura={580}
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Fechar
          </button>
          <button
            type="button"
            className="btn-primary"
            onClick={() => abrirModal('cliente', dados)}
          >
            Editar cadastro
          </button>
        </>
      }
    >
      <div className="ficha">
        <Avatar iniciais={dados.iniciais} size={52} />
        <div className="ficha__dados">
          <div className="mini-card__row">
            <span>Plano</span>
            <StatusBadge status={dados.plano} />
          </div>
          <div className="mini-card__row">
            <span>Ticket médio</span>
            <b>{formatarBRL(dados.ticket)}</b>
          </div>
          <div className="mini-card__row">
            <span>Última visita</span>
            <b>{dados.ultimaVisita}</b>
          </div>
        </div>
      </div>

      <h4 className="ficha__titulo">Histórico na agenda</h4>

      {historico.length ? (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Horário</th>
                <th>Serviço</th>
                <th>Barbeiro</th>
                <th>Valor</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {historico.map((a) => (
                <tr key={a.id}>
                  <td className="col-time">{a.horario}</td>
                  <td className="col-strong">{a.servico}</td>
                  <td className="col-nowrap">{a.barbeiro}</td>
                  <td className="col-money">{formatarBRL(a.valor)}</td>
                  <td>
                    <StatusBadge status={a.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="vazio">Nenhum agendamento para este cliente na agenda de hoje.</p>
      )}
    </Modal>
  );
}
