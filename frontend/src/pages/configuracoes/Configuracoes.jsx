import PageHeader from '../../js/components/PageHeader';
import Avatar from '../../js/components/Avatar';
import StatusBadge from '../../js/components/StatusBadge';
import { BlocoEstado } from '../../js/components/Estado';
import { IconLogout } from '../../js/components/Icons';
import { useApp } from '../../js/store/AppStore';
import { authApi } from '../../js/api/auth.api';
import { useCarregar } from '../../js/utils/useCarregar';
import { iniciaisDe } from '../../js/utils/formato';
import { data } from '../../js/utils/datas';
import '../../assets/css/pages/pages.css';

const rotulosPapel = { admin: 'Administrador', barbeiro: 'Barbeiro', cliente: 'Cliente' };

const permissoes = {
  admin: ['Agenda completa', 'Clientes e serviços', 'Estoque', 'Dashboard e relatórios'],
  barbeiro: ['Agenda completa', 'Concluir atendimentos', 'Consulta de clientes e serviços'],
  cliente: ['Marcar, remarcar e cancelar os próprios horários', 'Consulta de serviços']
};

export default function Configuracoes() {
  const { usuario, abrirModal, sair } = useApp();
  // Le do servidor, nao do localStorage: mostra o cadastro como esta hoje.
  const perfil = useCarregar(() => authApi.perfil(), []);
  const p = perfil.dados;

  return (
    <div className="page">
      <PageHeader titulo="Minha conta" subtitulo="Seus dados de acesso e o que o seu perfil pode fazer." />

      <div className="settings-grid">
        <section className="card card-pad">
          <h3>Dados do cadastro</h3>
          <BlocoEstado {...perfil} />
          {p && (
            <>
              <div className="ficha" style={{ marginBottom: 16 }}>
                <Avatar iniciais={iniciaisDe(p.nome)} size={52} />
                <div className="ficha__dados">
                  <div className="mini-card__row">
                    <span>Nome</span>
                    <b>{p.nome}</b>
                  </div>
                  <div className="mini-card__row">
                    <span>Situação</span>
                    <StatusBadge status={p.ativo ? 'Ativo' : 'Inativo'} />
                  </div>
                </div>
              </div>
              <div className="mini-card__rows">
                <div className="mini-card__row">
                  <span>E-mail</span>
                  <b>{p.email}</b>
                </div>
                <div className="mini-card__row">
                  <span>Telefone</span>
                  <b>{p.telefone || '—'}</b>
                </div>
                <div className="mini-card__row">
                  <span>Perfil</span>
                  <b>{rotulosPapel[p.papel]}</b>
                </div>
                <div className="mini-card__row">
                  <span>Cadastrado em</span>
                  <b>{data(p.criado_em)}</b>
                </div>
              </div>
            </>
          )}
        </section>

        <section className="card card-pad">
          <h3>Acesso</h3>
          {(permissoes[usuario.papel] || []).map((item) => (
            <div key={item} className="switch-row">
              <div>
                <strong>{item}</strong>
              </div>
              <StatusBadge status="Ativo" />
            </div>
          ))}

          <button
            type="button"
            className="btn-ghost"
            style={{ marginTop: 16 }}
            onClick={() =>
              abrirModal('confirmacao', {
                titulo: 'Sair do sistema',
                texto: 'Sua sessão será encerrada neste navegador.',
                rotuloConfirmar: 'Sair',
                aoConfirmar: sair
              })
            }
          >
            <IconLogout size={16} />
            Sair do sistema
          </button>
        </section>
      </div>
    </div>
  );
}
