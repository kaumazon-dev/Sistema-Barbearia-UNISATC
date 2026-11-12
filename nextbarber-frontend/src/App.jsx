import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import ModalHost from './components/ModalHost';
import Toaster from './components/Toaster';
import Dashboard from './pages/Dashboard';
import Agendamentos from './pages/Agendamentos';
import Clientes from './pages/Clientes';
import Barbeiros from './pages/Barbeiros';
import Servicos from './pages/Servicos';
import Relatorios from './pages/Relatorios';
import Configuracoes from './pages/Configuracoes';
import { AppProvider, useApp } from './state/AppStore';
import './App.css';

const paginas = {
  dashboard: Dashboard,
  agendamentos: Agendamentos,
  clientes: Clientes,
  barbeiros: Barbeiros,
  servicos: Servicos,
  relatorios: Relatorios,
  configuracoes: Configuracoes
};

function Layout() {
  const { pagina } = useApp();
  const Pagina = paginas[pagina] || Dashboard;

  return (
    <div className="app">
      <Sidebar />

      <div className="app__main">
        <Topbar />
        <main className="app__content">
          <Pagina />
        </main>
      </div>

      <ModalHost />
      <Toaster />
    </div>
  );
}

/**
 * Modelo de apresentacao: sem login e sem backend.
 * Todo o estado vive em memoria (src/state/AppStore.jsx) — F5 reinicia.
 */
export default function App() {
  return (
    <AppProvider>
      <Layout />
    </AppProvider>
  );
}
