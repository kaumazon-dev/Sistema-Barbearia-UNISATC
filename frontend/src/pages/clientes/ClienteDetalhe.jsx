import { useState } from 'react';
import Modal from '../../js/components/Modal';
import Avatar from '../../js/components/Avatar';
import StatusBadge from '../../js/components/StatusBadge';
import Paginacao from '../../js/components/Paginacao';
import { LinhaEstado } from '../../js/components/Estado';
import { useApp } from '../../js/store/AppStore';
import { agendamentosApi } from '../../js/api/agendamentos.api';
import { useCarregar } from '../../js/utils/useCarregar';
import { formatarBRL, iniciaisDe, STATUS } from '../../js/utils/formato';
import { data, hora } from '../../js/utils/datas';

/** Ficha do cliente com o historico de agendamentos (RF09). */
export default function ClienteDetalhe({ dados }) {
  const { usuario, fecharModal, abrirModal } = useApp();
  const [pagina, setPagina] = useState(1);

  const historico = useCarregar(
    () => agendamentosApi.listar({ clienteId: dados.id, pagina, porPagina: 8 }),
    [dados.id, pagina]
  );
  const itens = historico.dados?.itens || [];

  return (
    <Modal
      titulo={dados.nome}
      descricao={`${dados.telefone || 'sem telefone'} · ${dados.email}`}
      largura={640}
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Fechar
          </button>
          {usuario.papel === 'admin' && (
            <button type="button" className="btn-primary" onClick={() => abrirModal('cliente', dados)}>
              Editar cadastro
            </button>
          )}
        </>
      }
    >
      <div className="ficha">
        <Avatar iniciais={iniciaisDe(dados.nome)} size={52} />
        <div className="ficha__dados">
          <div className="mini-card__row">
            <span>Situação</span>
            <StatusBadge status={dados.ativo ? 'Ativo' : 'Inativo'} />
          </div>
          <div className="mini-card__row">
            <span>Agendamentos</span>
            <b>{historico.dados?.total ?? '—'}</b>
          </div>
          <div className="mini-card__row">
            <span>Cliente desde</span>
            <b>{data(dados.criado_em)}</b>
          </div>
        </div>
      </div>

      <h4 className="ficha__titulo">Histórico de agendamentos</h4>

      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Data</th>
              <th>Serviços</th>
              <th>Barbeiro</th>
              <th>Valor</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {itens.map((a) => (
              <tr key={a.id}>
                <td className="col-time">
                  {data(a.inicio)}
                  <span className="col-sub">{hora(a.inicio)}</span>
                </td>
                <td className="col-strong">{a.servicos.map((s) => s.nome).join(' + ')}</td>
                <td className="col-nowrap">{a.barbeiro.nome}</td>
                <td className="col-money">{formatarBRL(a.total)}</td>
                <td>
                  <StatusBadge status={STATUS[a.status]} />
                </td>
              </tr>
            ))}
            <LinhaEstado
              colunas={5}
              {...historico}
              vazio={itens.length === 0}
              textoVazio="Nenhum agendamento para este cliente."
            />
          </tbody>
        </table>
      </div>
      <Paginacao dados={historico.dados} onMudar={setPagina} />
    </Modal>
  );
}
