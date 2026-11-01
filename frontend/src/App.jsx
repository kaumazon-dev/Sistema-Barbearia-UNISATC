import Sidebar from './js/components/Sidebar';
import Topbar from './js/components/Topbar';
import ModalHost from './js/components/ModalHost';
import Toaster from './js/components/Toaster';
import Login from './pages/login/Login';
import Dashboard from './pages/dashboard/Dashboard';
import Agendamentos from './pages/agenda/Agendamentos';
import Clientes from './pages/clientes/Clientes';
import Barbeiros from './pages/barbeiros/Barbeiros';
import Servicos from './pages/servicos/Servicos';
import Estoque from './pages/estoque/Estoque';
import Relatorios from './pages/relatorios/Relatorios';
import Configuracoes from './pages/configuracoes/Configuracoes';
import { AppProvider, useApp } from './js/store/AppStore';
import './assets/css/components/layout.css';

const paginas = {
  dashboard: Dashboard,
  agendamentos: Agendamentos,
  clientes: Clientes,
  barbeiros: Barbeiros,
  servicos: Servicos,
  estoque: Estoque,
  relatorios: Relatorios,
  configuracoes: Configuracoes
};

function Layout() {
  const { usuario, pagina } = useApp();

  if (!usuario) {
    return (
      <>
        <Login />
        <Toaster />
      </>
    );
  }

  const Pagina = paginas[pagina] || Agendamentos;

  return (
    <div className="app">
      <Sidebar />

      <div className="app__main">
        <Topbar />
        <main className="app__content">
          {/* key: trocar de tela desmonta a anterior e zera filtros e paginas */}
          <Pagina key={pagina} />
        </main>
      </div>

      <ModalHost />
      <Toaster />
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <Layout />
    </AppProvider>
  );
}
