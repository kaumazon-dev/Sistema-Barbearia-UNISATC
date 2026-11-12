/**
 * Servidor local para apresentacao.
 *
 * Nao depende de npm install: usa so o que ja vem no Node.
 * Serve a pasta dist/ (build de producao) em http://localhost:3000
 *
 *   node servidor.js
 *   node servidor.js 8080      <- outra porta, se a 3000 estiver ocupada
 */

import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, extname, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const raiz = join(fileURLToPath(new URL('.', import.meta.url)), 'dist');
const porta = Number(process.argv[2]) || 3000;

if (!existsSync(join(raiz, 'index.html'))) {
  console.error('\n  A pasta dist/ nao foi encontrada.');
  console.error('  Use o arquivo NextBarber-apresentacao.html, ou rode "npm run build".\n');
  process.exit(1);
}

const tipos = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2'
};

const servidor = createServer(async (req, res) => {
  try {
    const caminhoUrl = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);

    // normalize + prefixo garantem que ninguem saia da pasta dist/
    let alvo = normalize(join(raiz, caminhoUrl));
    if (alvo !== raiz && !alvo.startsWith(raiz + sep)) {
      res.writeHead(403).end('403');
      return;
    }

    const info = await stat(alvo).catch(() => null);
    if (!info || info.isDirectory()) alvo = join(raiz, 'index.html');

    const corpo = await readFile(alvo);
    res.writeHead(200, {
      'Content-Type': tipos[extname(alvo).toLowerCase()] || 'application/octet-stream',
      'Cache-Control': 'no-cache'
    });
    res.end(corpo);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('404');
  }
});

servidor.on('error', (erro) => {
  if (erro.code === 'EADDRINUSE') {
    console.error(`\n  A porta ${porta} ja esta em uso.`);
    console.error(`  Tente outra: node servidor.js ${porta + 1}\n`);
  } else {
    console.error(erro.message);
  }
  process.exit(1);
});

// 127.0.0.1: acessivel so nesta maquina. Troque por '0.0.0.0' para abrir na rede.
servidor.listen(porta, '127.0.0.1', () => {
  const url = `http://localhost:${porta}`;
  console.log(`\n  NextBarber rodando em ${url}`);
  console.log('  Ctrl+C para parar.\n');

  const abrir =
    process.platform === 'win32'
      ? ['cmd', ['/c', 'start', '', url]]
      : process.platform === 'darwin'
        ? ['open', [url]]
        : ['xdg-open', [url]];

  try {
    const filho = spawn(abrir[0], abrir[1], { stdio: 'ignore', detached: true });
    // spawn emite o erro em evento, nao em throw: sem este handler o processo cai
    filho.on('error', () => {});
    filho.unref();
  } catch {
    // sem navegador automatico: o usuario abre a URL na mao
  }
});
