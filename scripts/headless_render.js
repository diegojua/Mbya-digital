import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

// 1. Criar um servidor HTTP simples para contornar restrições de CORS
const server = http.createServer((req, res) => {
  // Trata caminhos com decodificação de URL (ex: caracteres especiais)
  const decodedUrl = decodeURIComponent(req.url);
  let filePath = path.join(rootDir, decodedUrl === '/' ? 'workspace/preview.html' : decodedUrl);

  filePath = path.normalize(filePath);
  if (!filePath.startsWith(rootDir)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not Found');
    } else {
      let contentType = 'text/html';
      if (filePath.endsWith('.json')) contentType = 'application/json';
      else if (filePath.endsWith('.png')) contentType = 'image/png';
      else if (filePath.endsWith('.jpg') || filePath.endsWith('.jpeg')) contentType = 'image/jpeg';
      else if (filePath.endsWith('.js')) contentType = 'application/javascript';
      else if (filePath.endsWith('.css')) contentType = 'text/css';
      else if (filePath.endsWith('.svg')) contentType = 'image/svg+xml';

      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    }
  });
});

const PORT = 8124;
server.listen(PORT, async () => {
  console.log(`[Headless-Render] Servidor estático iniciado em http://localhost:${PORT}`);

  let chromium;
  try {
    // Tenta carregar o Playwright a partir do monorepo open-design
    let playwrightModule;
    const searchPaths = [
      'playwright',
      '../open-design/e2e/node_modules/playwright',
      '../open-design/node_modules/playwright',
      './open-design/e2e/node_modules/playwright',
      './open-design/node_modules/playwright'
    ];

    for (const searchPath of searchPaths) {
      try {
        playwrightModule = await import(searchPath);
        console.log(`[Headless-Render] Playwright carregado de: ${searchPath}`);
        break;
      } catch (e) {
        // Continue procurando
      }
    }

    if (!playwrightModule) {
      // Se não achar o import estático, tenta carregar o playwright-core ou do @playwright/test
      try {
        playwrightModule = await import('@playwright/test');
        console.log('[Headless-Render] Playwright carregado via @playwright/test');
      } catch (err) {
        throw new Error('Não foi possível encontrar a dependência do Playwright. Certifique-se de executar "pnpm install" no open-design/e2e ou na raiz.');
      }
    }

    const browser = await playwrightModule.chromium.launch({ headless: true });
    const page = await browser.newPage();

    // Resolução desktop premium de alta fidelidade
    await page.setViewportSize({ width: 1440, height: 1080 });

    console.log('[Headless-Render] Navegando até a Landing Page hidratada...');
    await page.goto(`http://localhost:${PORT}/workspace/preview.html`, { waitUntil: 'networkidle' });

    // Aguarda um pequeno delay para garantir que todas as transições de CSS e fetch local se consolidem
    await new Promise(resolve => setTimeout(resolve, 1500));

    const outputScreenshot = path.join(rootDir, 'workspace/campaign_preview.png');
    console.log(`[Headless-Render] Tirando captura de tela de alta resolução...`);
    await page.screenshot({ path: outputScreenshot, fullPage: true });

    console.log(`[Headless-Render] Screenshot gerado com sucesso em: ${outputScreenshot}`);
    await browser.close();
  } catch (error) {
    console.error('[Headless-Render] Falha durante o ciclo de renderização:', error.message || error);
  } finally {
    server.close(() => {
      console.log('[Headless-Render] Servidor estático finalizado.');
      process.exit(0);
    });
  }
});
