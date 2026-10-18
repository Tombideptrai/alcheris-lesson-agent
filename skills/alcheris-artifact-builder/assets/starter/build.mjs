// Builds one Alcheris artifact definition per entry in config.mjs, plus loose
// files for local preview. Usage: node build.mjs
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { artifacts } from './config.mjs';

const root = dirname(fileURLToPath(import.meta.url));
const read = (name) => readFile(join(root, name), 'utf8');
const [html, css, engine] = await Promise.all([read('index.html'), read('styles.css'), read('engine.js')]);

for (const { meta, config } of artifacts) {
  const script = `const CONFIG = ${JSON.stringify(config, null, 2)};\n\n${engine}`;
  const page = html.replace(/<title>[^<]*<\/title>/, `<title>${meta.title}</title>`);
  const definition = {
    type: 'artifact',
    title: meta.title,
    version: meta.version || '1.0.0',
    runtime: 'html_sandbox',
    entry: '/index.html',
    description: meta.description,
    appearance: { mode: 'inherit', tokenVersion: '1' },
    viewport: { preset: meta.preset || 'portrait', scrolling: 'none' },
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
  const size = Object.values(definition.files).reduce((n, f) => n + f.content.length, 0);
  console.log(`${meta.slug}: ${size} bytes -> dist/${meta.slug}/definition.json`);
}
