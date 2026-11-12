import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import MenuAcoes from '../components/MenuAcoes';
import { IconPlus, IconClock } from '../components/Icons';
import { useApp } from '../state/AppStore';
import { formatarBRL } from '../utils/formato';
import './pages.css';

export default function Servicos() {
  const { servicos, abrirModal, alternarServico } = useApp();

  const acoes = (s) => [
    { chave: 'editar', rotulo: 'Editar serviço', aoClicar: () => abrirModal('servico', s) },
    {
      chave: 'alternar',
      rotulo: s.ativo ? 'Desativar' : 'Reativar',
      aoClicar: () => alternarServico(s.id)
    }
  ];

  return (
    <div className="page">
      <PageHeader
        titulo="Serviços"
        subtitulo="Catálogo de serviços, duração e preço praticado."
        acao={
          <button type="button" className="btn-primary" onClick={() => abrirModal('servico')}>
            <IconPlus size={16} />
            Novo serviço
          </button>
        }
      />

      <section className="card panel">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Serviço</th>
                <th>Categoria</th>
                <th>Duração</th>
                <th>Preço</th>
                <th>Realizados (mês)</th>
                <th>Situação</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {servicos.map((s) => (
                <tr key={s.id} className={s.ativo ? '' : 'linha-inativa'}>
                  <td className="col-strong">{s.nome}</td>
                  <td>{s.categoria}</td>
                  <td>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                      <IconClock size={14} />
                      {s.duracao} min
                    </span>
                  </td>
                  <td className="col-money">{formatarBRL(s.preco)}</td>
                  <td>{s.realizados}</td>
                  <td>
                    <StatusBadge status={s.ativo ? 'Ativo' : 'Inativo'} />
                  </td>
                  <td className="col-acoes">
                    <MenuAcoes itens={acoes(s)} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
