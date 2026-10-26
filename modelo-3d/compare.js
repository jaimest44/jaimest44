const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome',
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const views = { sw: { p: [6.5, 0.4, 16.6], l: [18, -0.7, 12.5] }, w: { p: [1.5, 0.2, 10.5], l: [14, -0.4, 8.5] } };
  for (const [name, g] of [['proyecto', '-0.95'], ['variante', '-1.80']]) {
    const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
    await page.goto('file://' + path.join(__dirname, 'index.html') + '?g=' + g);
    await page.waitForFunction('window.ready===true');
    await page.addStyleTag({ content: '.panel,#bar,#note,#title{display:none!important}' });
    for (const [v, cam] of Object.entries(views)) {
      await page.evaluate(c => { window.CAM = c; window.renderAt(49); }, cam);
      await page.screenshot({ path: path.join(__dirname, `cmp_${v}_${name}.jpg`), type: 'jpeg', quality: 90 });
    }
    await page.close();
  }
  await b.close();
})();
