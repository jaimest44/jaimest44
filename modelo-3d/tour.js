const { chromium } = require('playwright-core');
const { spawn } = require('child_process');
const path = require('path'), fs = require('fs');
const mode = process.argv[2] || 'test', FPS = 25;
const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' +
  fs.readFileSync(path.join(__dirname, 'visor-3d.html'), 'utf8') + '</body></html>';
fs.writeFileSync(path.join(__dirname, 'wrapped.html'), html);
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome',
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => {
    const p = r.request().url().replace('https://cdn.jsdelivr.net/npm/three@0.160.0/', '');
    r.fulfill({ path: path.join(__dirname, 'node_modules/three', p), contentType: 'application/javascript' });
  });
  await page.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  page.on('pageerror', e => console.log('pageerror:', e.message));
  await page.goto('file://' + path.join(__dirname, 'wrapped.html'));
  await page.waitForSelector('#loading', { state: 'detached', timeout: 90000 });
  await page.addStyleTag({ content: '#panel,#compass,#labels{display:none!important}#app{grid-template-columns:1fr!important;inset:0!important}' });
  await page.waitForTimeout(1500);
  const DUR = await page.evaluate('window.TOUR_DUR');
  if (mode === 'test') {
    const times = process.argv[3].split(',').map(Number);
    for (const t of times) { const t0 = Date.now(); await page.evaluate(t => window.tourAt(t), t); await page.waitForTimeout(50);
      await page.screenshot({ path: path.join(__dirname, `tour_${String(t).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 85 }); console.log('t', t, Date.now() - t0, 'ms'); }
  } else {
    const out = process.argv[3];
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19', '-preset', 'medium', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const N = Math.round(DUR * FPS), start = Date.now();
    for (let f = 0; f < N; f++) {
      await page.evaluate(t => window.tourAt(t), f / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 50 === 0) console.log(`frame ${f}/${N} ${((Date.now() - start) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log('done', out);
  }
  await b.close();
})();
