import { useState } from 'react';
import PageHeader from '../../js/components/PageHeader';
import StatusBadge from '../../js/components/StatusBadge';
import Avatar from '../../js/components/Avatar';
import MenuAcoes from '../../js/components/MenuAcoes';
import { LinhaEstado } from '../../js/components/Estado';
import { useApp } from '../../js/store/AppStore';
import { authApi } from '../../js/api/auth.api';
import { useCarregar } from '../../js/utils/useCarregar';
import { iniciaisDe } from '../../js/utils/formato';
import { data } from '../../js/utils/datas';
import '../../assets/css/pages/pages.css';

const PAPEIS = [
  { valor: 'cliente', rotulo: 'Cliente', descricao: 'marca e acompanha só os próprios horários' },
  { valor: 'barbeiro', rotulo: 'Barbeiro', descricao: 'atende e vê a agenda completa da equipe' },
  { valor: 'admin', rotulo: 'Administrador', descricao: 'acesso total, inclusive estoque, dashboard e esta tela' }
];
const rotuloDe = (papel) => PAPEIS.find((p) => p.valor === papel)?.rotulo || papel;

const filtros = [{ valor: '', rotulo: 'Todos' }, ...PAPEIS.map((p) => ({ valor: p.valor, rotulo: `${p.rotulo}s` }))];

/**
 * Gestao de acesso: quem se cadastra entra como cliente e o admin decide
 * quem vira barbeiro ou administrador. Quem garante a regra e a API
 * (PATCH /auth/usuarios/<id>/papel); esta tela so oferece as opcoes.
 */
export default function Usuarios() {
  const { usuario: eu, abrirModal, alterarPapel } = useApp();
  const [papel, setPapel] = useState('');

  const consulta = useCarregar(() => authApi.listarUsuarios(papel), [papel]);
  const lista = [...(consulta.dados || [])].sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));

  const acoes = (u) =>
    PAPEIS.filter((p) => p.valor !== u.papel).map((p) => ({
      chave: p.valor,
      rotulo: `Tornar ${p.rotulo.toLowerCase()}`,
      aoClicar: () =>
        abrirModal('confirmacao', {
          titulo: `Tornar ${u.nome} ${p.rotulo.toLowerCase()}`,
          texto: `Como ${p.rotulo.toLowerCase()}, ${u.nome} ${p.descricao}. A mudança vale a partir do próximo login.`,
          rotuloConfirmar: 'Confirmar',
          aoConfirmar: () => alterarPapel(u, p.valor, p.rotulo.toLowerCase())
        })
    }));

  return (
    <div className="page">
      <PageHeader
        titulo="Usuários e acessos"
        subtitulo="Quem se cadastra entra como cliente. Aqui você define quem é barbeiro ou administrador."
      />

      <div className="filtros">
        <div className="toolbar">
          {filtros.map((f) => (
            <button
              key={f.rotulo}
              type="button"
              className={`chip ${papel === f.valor ? 'is-active' : ''}`}
              onClick={() => setPapel(f.valor)}
            >
              {f.rotulo}
            </button>
          ))}
        </div>
      </div>

      <section className="card panel">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Usuário</th>
                <th>E-mail</th>
                <th>Cadastro</th>
                <th>Papel</th>
                <th>Situação</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {lista.map((u) => (
                <tr key={u.id} className={u.ativo ? '' : 'linha-inativa'}>
                  <td>
                    <span className="cell-user">
                      <Avatar iniciais={iniciaisDe(u.nome)} size={34} tone="neutral" />
                      <strong>{u.nome}</strong>
                    </span>
                  </td>
                  <td>{u.email}</td>
                  <td>{data(u.criado_em)}</td>
                  <td>
                    <StatusBadge status={rotuloDe(u.papel)} />
                  </td>
                  <td>
                    <StatusBadge status={u.ativo ? 'Ativo' : 'Inativo'} />
                  </td>
                  <td className="col-acoes">
                    {u.id === eu.id ? <small>Você</small> : <MenuAcoes itens={acoes(u)} />}
                  </td>
                </tr>
              ))}
              <LinhaEstado colunas={6} {...consulta} vazio={lista.length === 0} textoVazio="Nenhum usuário encontrado." />
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
