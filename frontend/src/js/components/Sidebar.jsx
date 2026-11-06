import Avatar from './Avatar';
import {
  IconGrid,
  IconCalendarClock,
  IconUsers,
  IconUserCheck,
  IconScissors,
  IconXCircle,
  IconChartLine,
  IconSettings,
  IconLogout,
  IconBox
} from './Icons';
import { useApp } from '../store/AppStore';
import { podeAcessar } from '../store/sessao';
import { iniciaisDe } from '../utils/formato';
import '../../assets/css/components/Sidebar.css';

export const menu = [
  { id: 'dashboard', rotulo: 'Dashboard', Icone: IconGrid },
  { id: 'agendamentos', rotulo: 'Agendamentos', Icone: IconCalendarClock },
  { id: 'clientes', rotulo: 'Clientes', Icone: IconUsers },
  { id: 'barbeiros', rotulo: 'Barbeiros', Icone: IconScissors },
  { id: 'usuarios', rotulo: 'Usuários', Icone: IconUserCheck },
  { id: 'servicos', rotulo: 'Serviços', Icone: IconXCircle },
  { id: 'estoque', rotulo: 'Estoque', Icone: IconBox },
  { id: 'relatorios', rotulo: 'Relatórios', Icone: IconChartLine },
  { id: 'configuracoes', rotulo: 'Configurações', Icone: IconSettings }
];

const rotulosPapel = { admin: 'Administrador', barbeiro: 'Barbeiro', cliente: 'Cliente' };

export default function Sidebar() {
  const { usuario, pagina: paginaAtiva, navegar: onNavegar, abrirModal, sair } = useApp();
  const itens = menu.filter(({ id }) => podeAcessar(usuario.papel, id));

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
        {itens.map(({ id, rotulo, Icone }) => (
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
          <Avatar iniciais={iniciaisDe(usuario.nome)} size={36} />
          <span className="sidebar__user-info">
            <strong>{usuario.nome}</strong>
            <small>{rotulosPapel[usuario.papel]}</small>
          </span>
          <button
            type="button"
            className="sidebar__logout"
            title="Sair"
            aria-label="Sair"
            onClick={() =>
              abrirModal('confirmacao', {
                titulo: 'Sair do sistema',
                texto: 'Sua sessão será encerrada neste navegador.',
                rotuloConfirmar: 'Sair',
                aoConfirmar: sair
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
