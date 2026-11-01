# Front-end — NextBarber

Interface do Sistema de Gerenciamento de Barbearias, em React 18 + Vite, ligada
à API Flask (`/api/v1`). O visual veio do modelo do Figma (`nextbarber-frontend`);
os dados agora vêm todos da API.

## Como rodar

### Com Docker (junto com o backend)

```bash
docker compose up -d --build
```

Abra <http://localhost:8080>. O nginx serve o build e repassa `/api` para o
container `backend`, então front e API ficam na mesma origem e não há CORS.

### Em desenvolvimento (hot reload)

Com o backend de pé (`docker compose up -d db backend`):

```bash
cd frontend
npm install
npm run dev
```

Abra <http://localhost:5173>. O Vite repassa `/api` para `http://localhost:5000`
(veja `vite.config.js`). Para apontar para outro endereço:
`VITE_PROXY_API=http://outro-host:5000 npm run dev`.

### Produção fora do compose (Vercel)

Defina `VITE_API_URL` com a URL completa da API, por exemplo
`https://barbearia-api.onrender.com/api/v1`, e libere a origem do front em
`CORS_ORIGINS` no backend.

## Regras do front

- **Nenhuma tela chama `fetch`.** Tudo passa por `src/js/api/*.api.js`, que passa
  por `src/js/api/http.js`.
- **`http.js` é o único lugar que conhece a URL base e o token.** Ele também
  converte toda resposta de erro em `ErroApi { status, codigo, mensagem, campos }`.
  A tela decide o que fazer pelo `codigo`, nunca pelo texto.
- **401 com token = sessão expirada:** o `http.js` avisa o `AppStore`, que limpa
  a sessão e volta para o login.
- **Dinheiro chega como string** (`"35.90"`). `Number()` só para exibir; somar
  usa `somarDinheiro` (centavos inteiros).
- **Datas no fuso de Brasília**, como a API (`src/js/utils/datas.js`). O
  formulário monta `2026-11-03T09:00:00-03:00`, com o fuso que a API exige.
- O papel guardado no navegador só decide o que a tela **mostra**. Quem garante
  a permissão é o backend.

## Telas por papel

| Tela | admin | barbeiro | cliente |
|---|---|---|---|
| Login e cadastro | ✓ | ✓ | ✓ |
| Dashboard | ✓ | | |
| Agendamentos | agenda completa | agenda completa | só os próprios |
| Clientes | CRUD | consulta | |
| Barbeiros | ✓ | ✓ | |
| Serviços | CRUD | consulta | consulta |
| Estoque | ✓ | | |
| Relatórios (Chart.js) | ✓ | | |
| Configurações (minha conta) | ✓ | ✓ | ✓ |

A tela inicial é a primeira da coluna do papel. Abrir pela URL uma tela que o
papel não acessa (`#/estoque` como cliente) cai na tela inicial.

## Testes

```bash
cd frontend
npm test
```

Testes com Vitest em `tests/`, sem navegador e sem API (o `fetch` é simulado).
Cobrem as regras que quebram em silêncio: soma de dinheiro sem erro de centavo,
datas no fuso de Brasília em qualquer computador, erros da API por campo,
`http.js` (token, URL, sessão expirada) e as telas liberadas por papel.

## Estrutura

Segue o `CLAUDE.md`: uma pasta por tela, CSS de componente separado do CSS de
página, e o código que não é tela em `js/`.

```
frontend/
├── Dockerfile               # build com Node, imagem final nginx sem root
├── nginx.conf               # estaticos + proxy de /api para o backend
├── index.html
├── tests/                   # Vitest
└── src/
    ├── main.jsx             # ponto de entrada
    ├── App.jsx              # layout e troca de telas
    ├── pages/               # uma pasta por tela, com os modais dela
    │   ├── login/
    │   ├── dashboard/
    │   ├── agenda/          # Agendamentos + novo agendamento + remarcar
    │   ├── clientes/        # lista + cadastro + ficha com histórico
    │   ├── servicos/
    │   ├── estoque/         # produtos + entrada/saída + histórico
    │   ├── barbeiros/
    │   ├── relatorios/      # gráficos Chart.js
    │   └── configuracoes/
    ├── assets/css/
    │   ├── base.css         # tokens de cor, tipografia, badges
    │   ├── components/      # CSS de cada componente
    │   └── pages/           # CSS das telas
    └── js/
        ├── api/
        │   ├── http.js      # fetch centralizado, URL base, token, ErroApi
        │   └── *.api.js     # um módulo por recurso da API
        ├── components/      # Sidebar, Topbar, Modal, tabela, Grafico...
        ├── store/
        │   ├── sessao.js    # token + usuário, telas por papel
        │   └── AppStore.jsx # sessão, rota (#/tela), modal, avisos e ações
        └── utils/
            ├── useCarregar.js  # busca da tela + recarga depois de salvar
            ├── datas.js        # fuso de Brasília
            ├── formato.js      # moeda, quantidade, status
            └── erros.js        # ErroApi -> erros por campo do formulário
```
