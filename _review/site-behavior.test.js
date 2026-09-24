const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process');

const root = path.resolve(__dirname, '..');
const edge = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const failureServer = http.createServer((request, response) => {
  const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
  if (pathname === '/data/catalog-data.json') {
    response.writeHead(503, { 'Content-Type': 'application/json' });
    response.end('{"error":"unavailable"}');
    return;
  }
  const relative = pathname === '/' ? 'index.html' : pathname.replace(/^\//, '');
  const file = path.resolve(root, relative);
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    response.writeHead(404);
    response.end('Not found');
    return;
  }
  response.writeHead(200);
  fs.createReadStream(file).pipe(response);
});

async function readJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(String(response.status));
  return response.json();
}

async function run() {
  await new Promise((resolve) => failureServer.listen(8766, '127.0.0.1', resolve));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'ghl-edge-'));
  const edgeProcess = spawn(edge, [
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--remote-debugging-port=9223',
    '--user-data-dir=' + profile,
    'about:blank'
  ], { stdio: 'ignore' });

  try {
    let targets;
    for (let attempt = 0; attempt < 50; attempt += 1) {
      try {
        targets = await readJson('http://127.0.0.1:9223/json/list');
        if (targets.length) break;
      } catch {}
      await delay(100);
    }
    if (!targets || !targets.length) throw new Error('Edge debugging target unavailable');

    const pageTarget = targets.find((target) => target.type === 'page' && target.url === 'about:blank') ||
      targets.find((target) => target.type === 'page');
    if (!pageTarget) throw new Error('Edge page target unavailable');
    const socket = new WebSocket(pageTarget.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => {
      socket.onopen = resolve;
      socket.onerror = reject;
    });
    let sequence = 0;
    const pending = new Map();
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (!message.id || !pending.has(message.id)) return;
      const handlers = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) handlers.reject(new Error(message.error.message));
      else handlers.resolve(message.result);
    };
    const send = (method, params = {}) => new Promise((resolve, reject) => {
      const id = ++sequence;
      pending.set(id, { resolve, reject });
      socket.send(JSON.stringify({ id, method, params }));
    });
    const evaluate = async (expression) => {
      const result = await send('Runtime.evaluate', {
        expression,
        returnByValue: true,
        awaitPromise: true
      });
      if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
      return result.result.value;
    };
    const navigate = async (url) => {
      await send('Page.navigate', { url });
      for (let attempt = 0; attempt < 100; attempt += 1) {
        if (await evaluate("document.readyState === 'complete'")) return;
        await delay(100);
      }
      throw new Error('Navigation timed out: ' + url);
    };
    const waitFor = async (expression) => {
      for (let attempt = 0; attempt < 100; attempt += 1) {
        if (await evaluate(expression)) return;
        await delay(100);
      }
      throw new Error('Condition timed out: ' + expression);
    };

    await navigate('http://127.0.0.1:8765/catalog.html');
    await delay(1000);
    const initialDiagnostic = await evaluate("({url:location.href,ready:document.readyState,cards:document.querySelectorAll('.plugin-card').length,error:document.querySelector('#fieldMain [role=alert]')&&document.querySelector('#fieldMain [role=alert]').textContent,loader:document.querySelector('#siteLoader')&&document.querySelector('#siteLoader').textContent,field:document.querySelector('#fieldMain')&&document.querySelector('#fieldMain').innerHTML.slice(0,300)})");
    if (!initialDiagnostic.cards) console.error('Catalog diagnostic:', JSON.stringify(initialDiagnostic));
    await waitFor("document.querySelectorAll('.plugin-card').length > 0");
    await evaluate("document.querySelector('[data-mode=table]').click()");
    await waitFor("document.querySelectorAll('tr.row').length > 0");
    const opened = await evaluate("(()=>{const row=document.querySelector('tr.row');const repo=row.dataset.repo;row.click();return{repo,hash:location.hash,title:document.title,expanded:document.querySelector('tr.row[data-repo=\"'+repo+'\"]').getAttribute('aria-expanded')}})()");
    if (opened.hash !== '#' + opened.repo || opened.expanded !== 'true' || !opened.title.includes('Gap Hunter Labs')) {
      throw new Error('Table open state did not synchronize: ' + JSON.stringify(opened));
    }
    const closed = await evaluate("(()=>{document.querySelector('.dossier-close').click();return{hash:location.hash,title:document.title,expanded:[...document.querySelectorAll('tr.row')].some(row=>row.getAttribute('aria-expanded')==='true')}})()");
    if (closed.hash || closed.expanded || closed.title !== 'Plugin Catalog for IntelliJ & JetBrains IDEs | Gap Hunter Labs') {
      throw new Error('Table close state did not synchronize: ' + JSON.stringify(closed));
    }

    await navigate('http://127.0.0.1:8766/catalog.html');
    await waitFor("document.querySelector('#fieldMain [role=alert]') !== null");
    await waitFor("document.querySelector('#siteLoader') === null");
    const catalogFailure = await evaluate("(()=>{const alert=document.querySelector('#fieldMain [role=alert]');return{persistent:!!alert,title:!!alert.querySelector('h2'),retry:!!alert.querySelector('#catalogRetry'),fallback:!!alert.querySelector('a[href*=\"plugins.jetbrains.com/vendor\"]'),loader:!!document.querySelector('#siteLoader')}})()");
    if (!catalogFailure.persistent || !catalogFailure.title || !catalogFailure.retry || !catalogFailure.fallback || catalogFailure.loader) {
      throw new Error('Catalog failure UI incomplete: ' + JSON.stringify(catalogFailure));
    }

    await navigate('http://127.0.0.1:8766/index.html');
    await waitFor("document.querySelector('#heroSubtitle[role=alert]') !== null");
    const homeFailure = await evaluate("({alert:!!document.querySelector('#heroSubtitle[role=alert]'),retry:!!document.querySelector('#homeCatalogRetry'),fallback:!!document.querySelector('#stats a[href*=\"plugins.jetbrains.com/vendor\"]')})");
    if (!homeFailure.alert || !homeFailure.retry || !homeFailure.fallback) {
      throw new Error('Home failure UI incomplete: ' + JSON.stringify(homeFailure));
    }

    await send('Emulation.setDeviceMetricsOverride', {
      width: 390,
      height: 844,
      deviceScaleFactor: 1,
      mobile: true
    });
    await navigate('http://127.0.0.1:8765/methodology.html');
    const mobile = await evaluate("(()=>{const diagram=document.querySelector('.diagram-scroll');return{docOverflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,region:diagram.getAttribute('role'),tabIndex:diagram.tabIndex,label:diagram.getAttribute('aria-label'),centerDelta:Math.abs(diagram.scrollLeft-(diagram.scrollWidth-diagram.clientWidth)/2),svgWidth:document.querySelector('.decision-diagram').getBoundingClientRect().width}})()");
    if (mobile.docOverflow || mobile.region !== 'region' || mobile.tabIndex !== 0 || !/Arrow keys/.test(mobile.label) || mobile.centerDelta > 2 || mobile.svgWidth < 719) {
      throw new Error('Methodology mobile diagram failed: ' + JSON.stringify(mobile));
    }

    console.log(JSON.stringify({ opened, closed, catalogFailure, homeFailure, mobile }, null, 2));
    socket.close();
  } finally {
    edgeProcess.kill();
    failureServer.close();
  }
}

run().catch((error) => {
  console.error(error.stack || error);
  failureServer.close();
  process.exitCode = 1;
});
