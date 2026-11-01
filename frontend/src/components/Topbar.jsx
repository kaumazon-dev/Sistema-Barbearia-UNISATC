import { useEffect, useRef, useState } from 'react';
import { IconSearch, IconBell } from './Icons';
import { useApp } from '../state/AppStore';
import { clientesApi } from '../api/clientes.api';
import { servicosApi } from '../api/servicos.api';
import { produtosApi } from '../api/produtos.api';
import { useCarregar } from '../utils/useCarregar';
import { formatarBRL, formatarQuantidade } from '../utils/formato';
import { diaPorExtenso, hojeISO } from '../utils/datas';
import './Topbar.css';

export default function Topbar() {
  const { usuario, navegar, abrirModal } = useApp();
  const ehAdmin = usuario.papel === 'admin';
  const buscaClientes = usuario.papel !== 'cliente';

  const [busca, setBusca] = useState('');
  const [termo, setTermo] = useState('');
  const [sinoAberto, setSinoAberto] = useState(false);
  const areaBusca = useRef(null);
  const areaSino = useRef(null);

  // Espera o usuario parar de digitar antes de ir na API.
  useEffect(() => {
    const espera = setTimeout(() => setTermo(busca.trim()), 300);
    return () => clearTimeout(espera);
  }, [busca]);

  const pesquisando = termo.length >= 2;

  const { dados: resultados } = useCarregar(
    async () => {
      const [clientes, servicos] = await Promise.all([
        buscaClientes ? clientesApi.listar({ busca: termo, porPagina: 4 }) : null,
        servicosApi.listar()
      ]);
      const t = termo.toLowerCase();
      return {
        clientes: clientes?.itens || [],
        servicos: servicos.filter((s) => s.nome.toLowerCase().includes(t)).slice(0, 3)
      };
    },
    [termo],
    { ativo: pesquisando }
  );

  // Notificacoes do admin = produtos abaixo do minimo (RF27).
  const { dados: emFalta } = useCarregar(() => produtosApi.emFalta(), [], { ativo: ehAdmin });

  const totalResultados = resultados ? resultados.clientes.length + resultados.servicos.length : 0;

  /* Fecha os dois popovers ao clicar fora ou apertar ESC. */
  useEffect(() => {
    const aoClicarFora = (e) => {
      if (!areaBusca.current?.contains(e.target)) setBusca('');
      if (!areaSino.current?.contains(e.target)) setSinoAberto(false);
    };
    const aoTeclar = (e) => {
      if (e.key !== 'Escape') return;
      setBusca('');
      setSinoAberto(false);
    };
    document.addEventListener('mousedown', aoClicarFora);
    document.addEventListener('keydown', aoTeclar);
    return () => {
      document.removeEventListener('mousedown', aoClicarFora);
      document.removeEventListener('keydown', aoTeclar);
    };
  }, []);

  const irPara = (destino) => {
    setBusca('');
    navegar(destino);
  };

  return (
    <header className="topbar">
      <div className="topbar__busca-area" ref={areaBusca}>
        <label className="topbar__search">
          <IconSearch size={17} />
          <input
            type="text"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder={buscaClientes ? 'Buscar clientes ou serviços...' : 'Buscar serviços...'}
            aria-label="Buscar"
          />
        </label>

        {pesquisando && busca.trim() && resultados && (
          <div className="busca-resultados" role="listbox">
            {totalResultados === 0 && <p className="busca-vazio">Nada encontrado para “{termo}”.</p>}

            {resultados.clientes.length > 0 && (
              <section>
                <h4>Clientes</h4>
                {resultados.clientes.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => {
                      setBusca('');
                      abrirModal('clienteDetalhe', c);
                    }}
                  >
                    <strong>{c.nome}</strong>
                    <small>
                      {c.telefone || 'sem telefone'} · {c.email}
                    </small>
                  </button>
                ))}
              </section>
            )}

            {resultados.servicos.length > 0 && (
              <section>
                <h4>Serviços</h4>
                {resultados.servicos.map((s) => (
                  <button key={s.id} type="button" onClick={() => irPara('servicos')}>
                    <strong>{s.nome}</strong>
                    <small>
                      {s.duracao_minutos} min · {formatarBRL(s.preco)}
                    </small>
                  </button>
                ))}
              </section>
            )}
          </div>
        )}
      </div>

      <div className="topbar__right">
        <span className="topbar__unidade dot-label">NextBarber</span>

        {ehAdmin && (
          <div className="topbar__sino-area" ref={areaSino}>
            <button
              type="button"
              className="topbar__bell"
              aria-label="Produtos em falta"
              aria-expanded={sinoAberto}
              onClick={() => setSinoAberto((v) => !v)}
            >
              <IconBell size={18} />
              {emFalta?.length > 0 && <span className="topbar__bell-dot" />}
            </button>

            {sinoAberto && (
              <div className="notificacoes">
                <header>
                  <strong>Estoque baixo</strong>
                  <span>{emFalta?.length || 0} produtos</span>
                </header>
                {emFalta?.length ? (
                  <ul>
                    {emFalta.map((p) => (
                      <li key={p.id}>
                        <strong>{p.nome}</strong>
                        <p>
                          Restam {formatarQuantidade(p.quantidade_atual)} {p.unidade} · mínimo{' '}
                          {formatarQuantidade(p.estoque_minimo)} {p.unidade}
                        </p>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="busca-vazio">Nenhum produto abaixo do mínimo.</p>
                )}
                <button type="button" className="notificacoes__link" onClick={() => {
                  setSinoAberto(false);
                  navegar('estoque');
                }}>
                  Abrir estoque
                </button>
              </div>
            )}
          </div>
        )}

        <div className="topbar__data">
          <strong>{diaPorExtenso(hojeISO())}</strong>
          <small>Fuso de Brasília</small>
        </div>
      </div>
    </header>
  );
}
