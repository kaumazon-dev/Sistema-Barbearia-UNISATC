import { useMemo, useState } from 'react';
import PageHeader from '../../js/components/PageHeader';
import StatusBadge from '../../js/components/StatusBadge';
import MenuAcoes from '../../js/components/MenuAcoes';
import { LinhaEstado } from '../../js/components/Estado';
import { IconPlus, IconFilter } from '../../js/components/Icons';
import { useApp } from '../../js/store/AppStore';
import { agendamentosApi } from '../../js/api/agendamentos.api';
import { authApi } from '../../js/api/auth.api';
import { useCarregar } from '../../js/utils/useCarregar';
import { acoesDoAgendamento } from '../../js/utils/acoesAgendamento';
import { formatarBRL, STATUS } from '../../js/utils/formato';
import { hora, data, hojeISO, somarDias, diaPorExtenso } from '../../js/utils/datas';
import '../../assets/css/pages/pages.css';

const filtros = ['todos', ...Object.keys(STATUS)];

export default function Agendamentos() {
  const app = useApp();
  const { usuario, abrirModal } = app;
  const ehCliente = usuario.papel === 'cliente';

  const [dia, setDia] = useState(hojeISO());
  const [barbeiroId, setBarbeiroId] = useState('');
  const [filtro, setFiltro] = useState('todos');

  const { dados: barbeiros } = useCarregar(() => authApi.listarBarbeiros(), []);

  // Cliente ve todos os proprios horarios (RF21); a equipe ve a agenda por dia
  // e por barbeiro (RF17). Ate 100 por pagina cobre um dia inteiro.
  const agenda = useCarregar(
    () =>
      agendamentosApi.listar({
        dia: ehCliente ? undefined : dia,
        barbeiroId,
        porPagina: 100
      }),
    [dia, barbeiroId, ehCliente]
  );

  const todos = agenda.dados?.itens || [];
  const lista = useMemo(
    () => (filtro === 'todos' ? todos : todos.filter((a) => a.status === filtro)),
    [filtro, todos]
  );
  const contar = (status) =>
    status === 'todos' ? todos.length : todos.filter((a) => a.status === status).length;

  return (
    <div className="page">
      <PageHeader
        titulo={ehCliente ? 'Meus agendamentos' : 'Agendamentos'}
        subtitulo={
          ehCliente
            ? 'Seus horários marcados, concluídos e cancelados.'
            : `${todos.length} horários em ${diaPorExtenso(dia)}.`
        }
        acao={
          <button
            type="button"
            className="btn-primary"
            onClick={() => abrirModal('agendamento', { dia, barbeiroId })}
          >
            <IconPlus size={16} />
            {ehCliente ? 'Marcar horário' : 'Novo agendamento'}
          </button>
        }
      />

      <div className="filtros">
        {!ehCliente && (
          <>
            <div className="field">
              <label htmlFor="filtro-dia">Dia</label>
              <input id="filtro-dia" type="date" value={dia} onChange={(e) => e.target.value && setDia(e.target.value)} />
            </div>
            <button type="button" className="btn-ghost" onClick={() => setDia(somarDias(dia, -1))}>
              ‹ Anterior
            </button>
            <button type="button" className="btn-ghost" onClick={() => setDia(hojeISO())}>
              Hoje
            </button>
            <button type="button" className="btn-ghost" onClick={() => setDia(somarDias(dia, 1))}>
              Próximo ›
            </button>
          </>
        )}
        <div className="field">
          <label htmlFor="filtro-barbeiro">Barbeiro</label>
          <select id="filtro-barbeiro" value={barbeiroId} onChange={(e) => setBarbeiroId(e.target.value)}>
            <option value="">Todos</option>
            {(barbeiros || []).map((b) => (
              <option key={b.id} value={b.id}>
                {b.nome}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="toolbar">
        <span className="btn-ghost toolbar__rotulo">
          <IconFilter size={15} />
          Status
        </span>
        {filtros.map((f) => (
          <button
            key={f}
            type="button"
            className={`chip ${filtro === f ? 'is-active' : ''}`}
            onClick={() => setFiltro(f)}
          >
            {f === 'todos' ? 'Todos' : STATUS[f]} <span className="chip__contador">{contar(f)}</span>
          </button>
        ))}
      </div>

      <section className="card panel">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>{ehCliente ? 'Data e horário' : 'Horário'}</th>
                <th>Cliente</th>
                <th>Barbeiro</th>
                <th>Serviços</th>
                <th>Valor</th>
                <th>Status</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {lista.map((item) => (
                <tr key={item.id}>
                  <td className="col-time">
                    {ehCliente && <span className="col-sub">{data(item.inicio)}</span>}
                    {hora(item.inicio)}
                    <span className="col-sub">até {hora(item.fim)}</span>
                  </td>
                  <td className="col-strong">
                    {item.cliente.nome}
                    {item.observacao && <span className="col-sub">{item.observacao}</span>}
                  </td>
                  <td className="col-nowrap">{item.barbeiro.nome}</td>
                  <td>{item.servicos.map((s) => s.nome).join(' + ')}</td>
                  <td className="col-money">{formatarBRL(item.total)}</td>
                  <td>
                    <StatusBadge status={STATUS[item.status]} />
                  </td>
                  <td className="col-acoes">
                    {item.status === 'agendado' && <MenuAcoes itens={acoesDoAgendamento(item, app)} />}
                  </td>
                </tr>
              ))}
              <LinhaEstado
                colunas={7}
                {...agenda}
                vazio={lista.length === 0}
                textoVazio={filtro === 'todos' ? 'Nenhum agendamento neste dia.' : 'Nenhum agendamento com esse status.'}
              />
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
