import { useEffect, useState } from 'react';
import PageHeader from '../../js/components/PageHeader';
import StatusBadge from '../../js/components/StatusBadge';
import Avatar from '../../js/components/Avatar';
import MenuAcoes from '../../js/components/MenuAcoes';
import Paginacao from '../../js/components/Paginacao';
import { LinhaEstado } from '../../js/components/Estado';
import { IconPlus, IconSearch } from '../../js/components/Icons';
import { useApp } from '../../js/store/AppStore';
import { clientesApi } from '../../js/api/clientes.api';
import { useCarregar } from '../../js/utils/useCarregar';
import { iniciaisDe } from '../../js/utils/formato';
import { data } from '../../js/utils/datas';
import '../../assets/css/pages/pages.css';

const situacoes = [
  { valor: '', rotulo: 'Todos' },
  { valor: 'true', rotulo: 'Ativos' },
  { valor: 'false', rotulo: 'Inativos' }
];

export default function Clientes() {
  const { usuario, abrirModal, alternarCliente } = useApp();
  const ehAdmin = usuario.papel === 'admin';

  const [busca, setBusca] = useState('');
  const [termo, setTermo] = useState('');
  const [ativo, setAtivo] = useState('true');
  const [pagina, setPagina] = useState(1);

  // A busca e feita na API (RF08); espera parar de digitar.
  useEffect(() => {
    const espera = setTimeout(() => {
      setTermo(busca.trim());
      setPagina(1);
    }, 300);
    return () => clearTimeout(espera);
  }, [busca]);

  const consulta = useCarregar(
    () => clientesApi.listar({ busca: termo, ativo, pagina, porPagina: 15 }),
    [termo, ativo, pagina]
  );
  const lista = consulta.dados?.itens || [];

  const acoes = (c) => [
    { chave: 'ver', rotulo: 'Ver ficha', aoClicar: () => abrirModal('clienteDetalhe', c) },
    ...(c.ativo
      ? [{ chave: 'agendar', rotulo: 'Agendar horário', aoClicar: () => abrirModal('agendamento', { clienteId: c.id }) }]
      : []),
    ...(ehAdmin
      ? [
          { chave: 'editar', rotulo: 'Editar cadastro', aoClicar: () => abrirModal('cliente', c) },
          { chave: 'sep', separador: true },
          c.ativo
            ? {
                chave: 'desativar',
                rotulo: 'Desativar',
                perigo: true,
                aoClicar: () =>
                  abrirModal('confirmacao', {
                    titulo: 'Desativar cliente',
                    texto: `${c.nome} não poderá mais entrar no sistema nem receber agendamentos. O histórico continua guardado e o cadastro pode ser reativado.`,
                    rotuloConfirmar: 'Desativar',
                    aoConfirmar: () => alternarCliente(c)
                  })
              }
            : { chave: 'reativar', rotulo: 'Reativar', aoClicar: () => alternarCliente(c) }
        ]
      : [])
  ];

  return (
    <div className="page">
      <PageHeader
        titulo="Clientes"
        subtitulo={consulta.dados ? `${consulta.dados.total} clientes encontrados.` : 'Cadastro de clientes da barbearia.'}
        acao={
          ehAdmin && (
            <button type="button" className="btn-primary" onClick={() => abrirModal('cliente')}>
              <IconPlus size={16} />
              Novo cliente
            </button>
          )
        }
      />

      <div className="filtros">
        <label className="topbar__search">
          <IconSearch size={17} />
          <input
            type="text"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar por nome ou telefone..."
            aria-label="Buscar cliente"
          />
        </label>
        <div className="toolbar">
          {situacoes.map((s) => (
            <button
              key={s.rotulo}
              type="button"
              className={`chip ${ativo === s.valor ? 'is-active' : ''}`}
              onClick={() => {
                setAtivo(s.valor);
                setPagina(1);
              }}
            >
              {s.rotulo}
            </button>
          ))}
        </div>
      </div>

      <section className="card panel">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Telefone</th>
                <th>E-mail</th>
                <th>Cliente desde</th>
                <th>Situação</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {lista.map((c) => (
                <tr key={c.id} className={`linha-clicavel ${c.ativo ? '' : 'linha-inativa'}`}>
                  <td onClick={() => abrirModal('clienteDetalhe', c)}>
                    <span className="cell-user">
                      <Avatar iniciais={iniciaisDe(c.nome)} size={34} tone="neutral" />
                      <strong>{c.nome}</strong>
                    </span>
                  </td>
                  <td>{c.telefone || '—'}</td>
                  <td>{c.email}</td>
                  <td>{data(c.criado_em)}</td>
                  <td>
                    <StatusBadge status={c.ativo ? 'Ativo' : 'Inativo'} />
                  </td>
                  <td className="col-acoes">
                    <MenuAcoes itens={acoes(c)} />
                  </td>
                </tr>
              ))}
              <LinhaEstado colunas={6} {...consulta} vazio={lista.length === 0} textoVazio="Nenhum cliente encontrado." />
            </tbody>
          </table>
        </div>
        <Paginacao dados={consulta.dados} onMudar={setPagina} />
      </section>
    </div>
  );
}
