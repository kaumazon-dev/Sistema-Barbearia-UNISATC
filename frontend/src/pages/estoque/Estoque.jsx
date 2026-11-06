import { useMemo, useState } from 'react';
import PageHeader from '../../js/components/PageHeader';
import StatusBadge from '../../js/components/StatusBadge';
import MenuAcoes from '../../js/components/MenuAcoes';
import { LinhaEstado } from '../../js/components/Estado';
import { IconPlus, IconFilter } from '../../js/components/Icons';
import { useApp } from '../../js/store/AppStore';
import { produtosApi } from '../../js/api/produtos.api';
import { useCarregar } from '../../js/utils/useCarregar';
import { formatarQuantidade } from '../../js/utils/formato';
import '../../assets/css/pages/pages.css';

const filtros = [
  { id: 'ativos', rotulo: 'Ativos' },
  { id: 'falta', rotulo: 'Em falta' },
  { id: 'inativos', rotulo: 'Inativos' }
];

export default function Estoque() {
  const { abrirModal, alternarProduto } = useApp();
  const [filtro, setFiltro] = useState('ativos');

  const consulta = useCarregar(() => produtosApi.listar(), []);
  const produtos = consulta.dados || [];

  // em_falta vem calculado da API (RF27): quantidade <= minimo.
  const grupos = useMemo(
    () => ({
      ativos: produtos.filter((p) => p.ativo),
      falta: produtos.filter((p) => p.ativo && p.em_falta),
      inativos: produtos.filter((p) => !p.ativo)
    }),
    [produtos]
  );
  const lista = grupos[filtro];

  const acoes = (p) => [
    ...(p.ativo
      ? [
          { chave: 'entrada', rotulo: 'Registrar entrada', aoClicar: () => abrirModal('movimentacao', { ...p, tipo: 'entrada' }) },
          { chave: 'saida', rotulo: 'Registrar saída', aoClicar: () => abrirModal('movimentacao', { ...p, tipo: 'saida' }) }
        ]
      : []),
    { chave: 'historico', rotulo: 'Ver movimentações', aoClicar: () => abrirModal('historicoProduto', p) },
    { chave: 'sep', separador: true },
    { chave: 'editar', rotulo: 'Editar produto', aoClicar: () => abrirModal('produto', p) },
    p.ativo
      ? {
          chave: 'desativar',
          rotulo: 'Desativar',
          perigo: true,
          aoClicar: () =>
            abrirModal('confirmacao', {
              titulo: 'Desativar produto',
              texto: `${p.nome} para de aceitar entradas e saídas. O histórico de movimentações continua guardado.`,
              rotuloConfirmar: 'Desativar',
              aoConfirmar: () => alternarProduto(p)
            })
        }
      : { chave: 'reativar', rotulo: 'Reativar', aoClicar: () => alternarProduto(p) }
  ];

  return (
    <div className="page">
      <PageHeader
        titulo="Estoque"
        subtitulo="A quantidade só muda por entrada ou saída, e toda mudança fica no histórico."
        acao={
          <button type="button" className="btn-primary" onClick={() => abrirModal('produto')}>
            <IconPlus size={16} />
            Novo produto
          </button>
        }
      />

      <div className="toolbar">
        <span className="btn-ghost toolbar__rotulo">
          <IconFilter size={15} />
          Mostrar
        </span>
        {filtros.map((f) => (
          <button
            key={f.id}
            type="button"
            className={`chip ${filtro === f.id ? 'is-active' : ''}`}
            onClick={() => setFiltro(f.id)}
          >
            {f.rotulo} <span className="chip__contador">{grupos[f.id].length}</span>
          </button>
        ))}
      </div>

      <section className="card panel">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Produto</th>
                <th>Quantidade</th>
                <th>Mínimo</th>
                <th>Situação</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {lista.map((p) => (
                <tr key={p.id} className={`${p.ativo ? '' : 'linha-inativa'} ${p.ativo && p.em_falta ? 'linha-alerta' : ''}`}>
                  <td className="col-strong">
                    {p.nome}
                    <span className="col-sub">unidade: {p.unidade}</span>
                  </td>
                  <td className="col-money">
                    {formatarQuantidade(p.quantidade_atual)} {p.unidade}
                  </td>
                  <td>
                    {formatarQuantidade(p.estoque_minimo)} {p.unidade}
                  </td>
                  <td>
                    <StatusBadge status={!p.ativo ? 'Inativo' : p.em_falta ? 'Em falta' : 'Em dia'} />
                  </td>
                  <td className="col-acoes">
                    <MenuAcoes itens={acoes(p)} />
                  </td>
                </tr>
              ))}
              <LinhaEstado
                colunas={5}
                {...consulta}
                vazio={lista.length === 0}
                textoVazio={filtro === 'falta' ? 'Nenhum produto abaixo do mínimo.' : 'Nenhum produto aqui.'}
              />
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
