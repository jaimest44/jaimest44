const { chromium } = require('playwright-core');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const dir = __dirname;
const mode = process.argv[2] || 'test';
const FPS = 30;

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome',
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  page.on('console', m => console.log('console:', m.text()));
  page.on('pageerror', e => console.log('pageerror:', e.message));
  await page.goto('file://' + path.join(dir, 'index.html') + (process.env.Q || ''));
  await page.waitForFunction('window.ready===true', null, { timeout: 60000 });
  const DUR = await page.evaluate('window.DUR');

  if (mode === 'test') {
    const times = (process.argv[3] || '1,7,15,19,23,29,32,36,40,45,50,56').split(',').map(Number);
    fs.mkdirSync(path.join(dir, 'test'), { recursive: true });
    for (const t of times) {
      const t0 = Date.now();
      await page.evaluate(t => window.renderAt(t), t);
      await page.screenshot({ path: path.join(dir, 'test', `t${String(t).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 85 });
      console.log('t', t, Date.now() - t0, 'ms');
    }
  } else {
    const out = process.argv[3];
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const N = Math.round(DUR * FPS);
    const start = Date.now();
    for (let f = 0; f < N; f++) {
      await page.evaluate(t => window.renderAt(t), f / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 60 === 0) console.log(`frame ${f}/${N} ${((Date.now() - start) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    console.log('done', out);
  }
  await browser.close();
})();
