// Builds one Alcheris artifact package per config, plus a local preview folder.
// Usage: node build.mjs
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { trend, staticGraph } from './configs.mjs';

const root = dirname(fileURLToPath(import.meta.url));
const read = (name) => readFile(join(root, name), 'utf8');
const [html, css, engine] = await Promise.all([read('index.html'), read('styles.css'), read('engine.js')]);

for (const { meta, config } of [trend, staticGraph]) {
  const script = `const CONFIG = ${JSON.stringify(config, null, 2)};\n\n${engine}`;
  const page = html.replace('<title>Graph skins</title>', `<title>${meta.title}</title>`);
  const definition = {
    type: 'artifact',
    title: meta.title,
    version: '1.0.0',
    runtime: 'html_sandbox',
    entry: '/index.html',
    description: meta.description,
    appearance: { mode: 'inherit', tokenVersion: '1' },
    viewport: { preset: 'portrait', scrolling: 'none' },
    renderTargets: { editorBlock: true, fullPanel: true, playerDesktop: true, playerMobile: true },
    mobileBehavior: { mode: 'full', layout: 'responsive', minWidth: 320 },
    completion: { type: 'manual' },
    submission: { enabled: false, mode: 'none', storage: 'alcheris_managed' },
    analytics: { events: ['block_viewed', 'block_interacted', 'block_completed'] },
    security: { sandbox: true, allowNetwork: false, allowStorage: false, allowClipboard: false },
    files: {
      '/index.html': { type: 'text/html', content: page },
      '/styles.css': { type: 'text/css', content: css },
      '/script.js': { type: 'application/javascript', content: script },
    },
  };

  const outDir = join(root, 'dist', meta.slug);
  await mkdir(outDir, { recursive: true });
  await writeFile(join(outDir, 'index.html'), page);
  await writeFile(join(outDir, 'styles.css'), css);
  await writeFile(join(outDir, 'script.js'), script);
  await writeFile(join(outDir, 'definition.json'), JSON.stringify(definition));
  const pkg = { format: 'alcheris_artifact', formatVersion: '1.0', name: meta.title, description: meta.description, category: 'simulation', tags: meta.tags, definition };
  await writeFile(join(root, `${meta.slug}.alcheris-artifact.json`), `${JSON.stringify(pkg, null, 2)}\n`);
  const size = Object.values(definition.files).reduce((n, f) => n + f.content.length, 0);
  console.log(`${meta.slug}: ${size} bytes`);
}
