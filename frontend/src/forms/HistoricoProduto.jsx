import { useState } from 'react';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import Paginacao from '../components/Paginacao';
import { LinhaEstado } from '../components/Estado';
import { useApp } from '../state/AppStore';
import { produtosApi } from '../api/produtos.api';
import { useCarregar } from '../utils/useCarregar';
import { formatarQuantidade } from '../utils/formato';
import { data, hora } from '../utils/datas';

const tipos = [
  { valor: '', rotulo: 'Todas' },
  { valor: 'entrada', rotulo: 'Entradas' },
  { valor: 'saida', rotulo: 'Saídas' }
];

/** Historico de movimentacoes do produto, da mais recente para a mais antiga. */
export default function HistoricoProduto({ dados }) {
  const { fecharModal } = useApp();
  const [tipo, setTipo] = useState('');
  const [pagina, setPagina] = useState(1);

  const consulta = useCarregar(
    () => produtosApi.movimentacoes(dados.id, { tipo, pagina, porPagina: 10 }),
    [dados.id, tipo, pagina]
  );
  const itens = consulta.dados?.itens || [];

  return (
    <Modal
      titulo={`Movimentações · ${dados.nome}`}
      descricao={`Saldo atual: ${formatarQuantidade(dados.quantidade_atual)} ${dados.unidade}`}
      largura={680}
      onFechar={fecharModal}
    >
      <div className="toolbar" style={{ marginBottom: 12 }}>
        {tipos.map((t) => (
          <button
            key={t.rotulo}
            type="button"
            className={`chip ${tipo === t.valor ? 'is-active' : ''}`}
            onClick={() => {
              setTipo(t.valor);
              setPagina(1);
            }}
          >
            {t.rotulo}
          </button>
        ))}
      </div>

      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Quando</th>
              <th>Tipo</th>
              <th>Quantidade</th>
              <th>Motivo</th>
              <th>Responsável</th>
            </tr>
          </thead>
          <tbody>
            {itens.map((m) => (
              <tr key={m.id}>
                <td className="col-time">
                  {data(m.criado_em)}
                  <span className="col-sub">{hora(m.criado_em)}</span>
                </td>
                <td>
                  <StatusBadge status={m.tipo === 'entrada' ? 'Entrada' : 'Saída'} />
                </td>
                <td className="col-money">
                  {m.tipo === 'entrada' ? '+' : '−'}
                  {formatarQuantidade(m.quantidade)} {dados.unidade}
                </td>
                <td>{m.motivo || '—'}</td>
                <td className="col-nowrap">{m.usuario.nome}</td>
              </tr>
            ))}
            <LinhaEstado
              colunas={5}
              {...consulta}
              vazio={itens.length === 0}
              textoVazio="Nenhuma movimentação registrada."
            />
          </tbody>
        </table>
      </div>
      <Paginacao dados={consulta.dados} onMudar={setPagina} />
    </Modal>
  );
}
