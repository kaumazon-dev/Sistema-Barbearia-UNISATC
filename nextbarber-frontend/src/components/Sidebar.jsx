import Avatar from './Avatar';
import {
  IconGrid,
  IconCalendarClock,
  IconUsers,
  IconScissors,
  IconXCircle,
  IconChartLine,
  IconSettings,
  IconLogout
} from './Icons';
import { usuario } from '../data/mock';
import { useApp } from '../state/AppStore';
import './Sidebar.css';

export const menu = [
  { id: 'dashboard', rotulo: 'Dashboard', Icone: IconGrid },
  { id: 'agendamentos', rotulo: 'Agendamentos', Icone: IconCalendarClock },
  { id: 'clientes', rotulo: 'Clientes', Icone: IconUsers },
  { id: 'barbeiros', rotulo: 'Barbeiros', Icone: IconScissors },
  { id: 'servicos', rotulo: 'Serviços', Icone: IconXCircle },
  { id: 'relatorios', rotulo: 'Relatórios', Icone: IconChartLine },
  { id: 'configuracoes', rotulo: 'Configurações', Icone: IconSettings }
];

export default function Sidebar() {
  const { pagina: paginaAtiva, navegar: onNavegar, abrirModal, avisar } = useApp();

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__logo">
          <IconScissors size={18} />
        </span>
        <span className="sidebar__brand-text">
          <strong>NextBarber</strong>
          <small>PREMIUM HUB</small>
        </span>
      </div>

      <nav className="sidebar__nav" aria-label="Navegação principal">
        {menu.map(({ id, rotulo, Icone }) => (
          <button
            key={id}
            type="button"
            className={`sidebar__item ${paginaAtiva === id ? 'is-active' : ''}`}
            onClick={() => onNavegar(id)}
            aria-current={paginaAtiva === id ? 'page' : undefined}
          >
            <Icone size={18} />
            <span>{rotulo}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar__footer">
        <div className="sidebar__user">
          <Avatar iniciais={usuario.iniciais} size={36} />
          <span className="sidebar__user-info">
            <strong>{usuario.nome}</strong>
            <small>{usuario.papel}</small>
          </span>
          <button
            type="button"
            className="sidebar__logout"
            title="Sair"
            aria-label="Sair"
            onClick={() =>
              abrirModal('confirmacao', {
                titulo: 'Sair do sistema',
                texto: 'Este protótipo não tem login, então sair apenas fecharia a sessão fictícia.',
                rotuloConfirmar: 'Entendi',
                aoConfirmar: () => avisar('Logout é só demonstrativo neste modelo.')
              })
            }
          >
            <IconLogout size={18} />
          </button>
        </div>
      </div>
    </aside>
  );
}
