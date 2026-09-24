// render_og.js -- renderiza un HTML de pipeline/og_plugin_template.html
// (ya con los tokens @@...@@ sustituidos por build_og_images.py) a un
// PNG de 1200x630 via Chromium headless.
//
// Requiere puppeteer-core instalado en pipeline/node_modules (ver
// pipeline/package.json) y un Chromium/Chrome/Edge real en el sistema
// -- por defecto usa Edge en Windows, override con
// PUPPETEER_EXECUTABLE_PATH si hace falta otro binario u otro SO.
//
// Uso: node pipeline/render_og.js <input.html> <output.png>

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const DEFAULT_EXECUTABLE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';

async function main() {
  const [, , inputHtml, outputPng] = process.argv;
  if (!inputHtml || !outputPng) {
    console.error('uso: node render_og.js <input.html> <output.png>');
    process.exit(1);
  }
  const absHtml = path.resolve(inputHtml);
  if (!fs.existsSync(absHtml)) {
    console.error('no existe: ' + absHtml);
    process.exit(1);
  }
  const executablePath = process.env.PUPPETEER_EXECUTABLE_PATH || DEFAULT_EXECUTABLE;

  const browser = await puppeteer.launch({ executablePath, headless: true });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 630, deviceScaleFactor: 1 });
    await page.goto('file://' + absHtml.replace(/\\/g, '/'), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: outputPng, type: 'png' });
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error('SCRIPT FAILED:', err);
  process.exit(1);
});
