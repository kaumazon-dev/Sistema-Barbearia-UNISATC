/**
 * Junta o resultado de dist-standalone/ em um unico arquivo HTML.
 * Sem dependencias: roda com o Node puro.
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const dir = 'dist-standalone';
const saida = 'NextBarber-apresentacao.html';

if (!existsSync(join(dir, 'app.js'))) {
  console.error(`Rode "npm run build -- --config vite.config.standalone.js" antes.`);
  process.exit(1);
}

const js = readFileSync(join(dir, 'app.js'), 'utf8');
const css = existsSync(join(dir, 'app.css'))
  ? readFileSync(join(dir, 'app.css'), 'utf8')
  : '';

// </script> dentro do bundle quebraria a tag: escapamos.
const jsSeguro = js.replace(/<\/script>/gi, '<\\/script>');

const html = `<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>NextBarber — Premium Hub</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
      rel="stylesheet"
    />
    <style>
${css}
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script>
${jsSeguro}
    </script>
  </body>
</html>
`;

writeFileSync(saida, html, 'utf8');
console.log(`${saida} gerado (${(html.length / 1024).toFixed(0)} kB).`);
