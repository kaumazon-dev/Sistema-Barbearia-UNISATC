import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import ModalHost from './components/ModalHost';
import Toaster from './components/Toaster';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Agendamentos from './pages/Agendamentos';
import Clientes from './pages/Clientes';
import Barbeiros from './pages/Barbeiros';
import Servicos from './pages/Servicos';
import Estoque from './pages/Estoque';
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
