import PageHeader from '../../js/components/PageHeader';
import StatusBadge from '../../js/components/StatusBadge';
import MenuAcoes from '../../js/components/MenuAcoes';
import { LinhaEstado } from '../../js/components/Estado';
import { IconPlus, IconClock } from '../../js/components/Icons';
import { useApp } from '../../js/store/AppStore';
import { servicosApi } from '../../js/api/servicos.api';
import { useCarregar } from '../../js/utils/useCarregar';
import { formatarBRL } from '../../js/utils/formato';
import '../../assets/css/pages/pages.css';

export default function Servicos() {
  const { usuario, abrirModal, alternarServico } = useApp();
  const ehAdmin = usuario.papel === 'admin';

  // Quem nao e admin so recebe os ativos: a propria API filtra.
  const consulta = useCarregar(() => servicosApi.listar(), []);
  const servicos = consulta.dados || [];

  const acoes = (s) => [
    { chave: 'editar', rotulo: 'Editar serviço', aoClicar: () => abrirModal('servico', s) },
    s.ativo
      ? {
          chave: 'desativar',
          rotulo: 'Desativar',
          perigo: true,
          aoClicar: () =>
            abrirModal('confirmacao', {
              titulo: 'Desativar serviço',
              texto: `${s.nome} deixa de aparecer ao marcar horário. Agendamentos já feitos não mudam.`,
              rotuloConfirmar: 'Desativar',
              aoConfirmar: () => alternarServico(s)
            })
        }
      : { chave: 'reativar', rotulo: 'Reativar', aoClicar: () => alternarServico(s) }
  ];

  return (
    <div className="page">
      <PageHeader
        titulo="Serviços"
        subtitulo="Catálogo de serviços, duração e preço praticado."
        acao={
          ehAdmin && (
            <button type="button" className="btn-primary" onClick={() => abrirModal('servico')}>
              <IconPlus size={16} />
              Novo serviço
            </button>
          )
        }
      />

      <section className="card panel">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Serviço</th>
                <th>Duração</th>
                <th>Preço</th>
                <th>Situação</th>
                {ehAdmin && <th aria-label="Ações" />}
              </tr>
            </thead>
            <tbody>
              {servicos.map((s) => (
                <tr key={s.id} className={s.ativo ? '' : 'linha-inativa'}>
                  <td className="col-strong">{s.nome}</td>
                  <td>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                      <IconClock size={14} />
                      {s.duracao_minutos} min
                    </span>
                  </td>
                  <td className="col-money">{formatarBRL(s.preco)}</td>
                  <td>
                    <StatusBadge status={s.ativo ? 'Ativo' : 'Inativo'} />
                  </td>
                  {ehAdmin && (
                    <td className="col-acoes">
                      <MenuAcoes itens={acoes(s)} />
                    </td>
                  )}
                </tr>
              ))}
              <LinhaEstado
                colunas={ehAdmin ? 5 : 4}
                {...consulta}
                vazio={servicos.length === 0}
                textoVazio="Nenhum serviço cadastrado."
              />
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
