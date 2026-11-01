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

- **Nenhuma tela chama `fetch`.** Tudo passa por `src/api/*.api.js`, que passa
  por `src/api/http.js`.
- **`http.js` é o único lugar que conhece a URL base e o token.** Ele também
  converte toda resposta de erro em `ErroApi { status, codigo, mensagem, campos }`.
  A tela decide o que fazer pelo `codigo`, nunca pelo texto.
- **401 com token = sessão expirada:** o `http.js` avisa o `AppStore`, que limpa
  a sessão e volta para o login.
- **Dinheiro chega como string** (`"35.90"`). `Number()` só para exibir; somar
  usa `somarDinheiro` (centavos inteiros).
- **Datas no fuso de Brasília**, como a API (`src/utils/datas.js`). O
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

## Estrutura

```
src/
├── api/
│   ├── http.js              # fetch centralizado, URL base, token, ErroApi
│   └── *.api.js             # um módulo por recurso da API
├── store/sessao.js          # token + usuário no localStorage, telas por papel
├── state/AppStore.jsx       # sessão, rota (#/tela), modal, avisos e ações
├── pages/                   # uma tela por item do menu + Login
├── forms/                   # modais de cadastro, remarcação, movimentação...
├── components/              # Sidebar, Topbar, tabela, Modal, Grafico (Chart.js)...
├── utils/
│   ├── useCarregar.js       # busca da tela + recarga depois de salvar
│   ├── datas.js             # fuso de Brasília
│   ├── formato.js           # moeda, quantidade, status
│   └── erros.js             # ErroApi -> erros por campo do formulário
└── styles/                  # tokens de cor e tabela
```
