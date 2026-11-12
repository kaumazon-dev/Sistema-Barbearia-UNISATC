import { useMemo, useState } from 'react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import Avatar from '../components/Avatar';
import MenuAcoes from '../components/MenuAcoes';
import { IconPlus, IconSearch } from '../components/Icons';
import { unidade } from '../data/mock';
import { useApp } from '../state/AppStore';
import { formatarBRL } from '../utils/formato';
import './pages.css';

export default function Clientes() {
  const { clientes, abrirModal, removerCliente } = useApp();
  const [termo, setTermo] = useState('');

  const lista = useMemo(() => {
    const t = termo.trim().toLowerCase();
    if (!t) return clientes;
    return clientes.filter(
      (c) => c.nome.toLowerCase().includes(t) || c.telefone.includes(t)
    );
  }, [termo, clientes]);

  const acoes = (c) => [
    { chave: 'ver', rotulo: 'Ver ficha', aoClicar: () => abrirModal('clienteDetalhe', c) },
    { chave: 'editar', rotulo: 'Editar cadastro', aoClicar: () => abrirModal('cliente', c) },
    {
      chave: 'agendar',
      rotulo: 'Agendar horário',
      aoClicar: () => abrirModal('agendamento', { clienteId: c.id })
    },
    { chave: 'sep', separador: true },
    {
      chave: 'excluir',
      rotulo: 'Excluir',
      perigo: true,
      aoClicar: () =>
        abrirModal('confirmacao', {
          titulo: 'Excluir cliente',
          texto: `${c.nome} sairá da lista. Os agendamentos ficam sem cliente vinculado.`,
          aoConfirmar: () => removerCliente(c.id)
        })
    }
  ];

  return (
    <div className="page">
      <PageHeader
        titulo="Clientes"
        subtitulo={`${clientes.length} clientes cadastrados na ${unidade.nome}.`}
        acao={
          <button type="button" className="btn-primary" onClick={() => abrirModal('cliente')}>
            <IconPlus size={16} />
            Novo cliente
          </button>
        }
      />

      <label className="topbar__search" style={{ maxWidth: 360 }}>
        <IconSearch size={17} />
        <input
          type="text"
          value={termo}
          onChange={(e) => setTermo(e.target.value)}
          placeholder="Buscar por nome ou telefone..."
          aria-label="Buscar cliente"
        />
      </label>

      <section className="card panel">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Telefone</th>
                <th>Última visita</th>
                <th>Visitas</th>
                <th>Ticket médio</th>
                <th>Plano</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {lista.map((c) => (
                <tr key={c.id} className="linha-clicavel">
                  <td onClick={() => abrirModal('clienteDetalhe', c)}>
                    <span className="cell-user">
                      <Avatar iniciais={c.iniciais} size={34} tone="neutral" />
                      <strong>{c.nome}</strong>
                    </span>
                  </td>
                  <td>{c.telefone}</td>
                  <td>{c.ultimaVisita}</td>
                  <td>{c.visitas}</td>
                  <td className="col-money">{formatarBRL(c.ticket)}</td>
                  <td>
                    <StatusBadge status={c.plano} />
                  </td>
                  <td className="col-acoes">
                    <MenuAcoes itens={acoes(c)} />
                  </td>
                </tr>
              ))}
              {lista.length === 0 && (
                <tr>
                  <td colSpan={7} className="vazio">
                    Nenhum cliente encontrado.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
