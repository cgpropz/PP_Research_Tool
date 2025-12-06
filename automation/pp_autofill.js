const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const STORAGE_PATH = path.resolve(__dirname, 'storage-state.json');

function decodeCgpp(cgpp){
  try{
    if (!cgpp) throw new Error('Empty cgpp');
    // Sanitize: strip quotes/whitespace and convert URL-safe base64 to standard
    let b64 = String(cgpp).trim().replace(/^"|"$/g,'');
    b64 = b64.replace(/\s+/g,'').replace(/-/g,'+').replace(/_/g,'/');
    // Pad if needed
    const pad = b64.length % 4;
    if (pad) b64 += '='.repeat(4-pad);
    const json = decodeURIComponent(escape(Buffer.from(b64, 'base64').toString('binary')));
    const parsed = JSON.parse(json);
    if (!parsed || !Array.isArray(parsed.items)) return null;
    return parsed.items;
  }catch(e){
    console.warn('[PP-AUTO]', 'Failed to parse cgpp', e.message);
    return null;
  }
}

function readSlipFromFile(fp){
  const raw = fs.readFileSync(fp, 'utf8');
  const parsed = JSON.parse(raw);
  if (Array.isArray(parsed.items)) return parsed.items;
  if (Array.isArray(parsed)) return parsed;
  throw new Error('Invalid slip file format');
}

function norm(s){ return String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim(); }

async function selectNBA(page){
  // Try common selectors and labels for NBA/Basketball
  const tries = [
    '[data-testid*="nba" i]', '[aria-label*="NBA" i]', '[data-sport*="nba" i]', '[href*="nba" i]',
    '[data-testid*="basketball" i]', '[aria-label*="Basketball" i]', '[data-testid*="chip" i]'
  ];
  for (const sel of tries){
    const els = await page.$$(sel);
    for (const el of els){
      const txt = (await el.textContent()||'') + (await el.getAttribute('data-testid')||'') + (await el.getAttribute('aria-label')||'');
      if (/\b(NBA|Basketball)\b/i.test(txt)) { await el.click(); await page.waitForTimeout(600); return true; }
    }
  }
  // Fallback by text (single-line XPath to avoid syntax errors)
  const byText = await page.$("xpath=//button[normalize-space()='NBA' or contains(translate(.,'BASKETBALL','basketball'),'basketball')] | //a[normalize-space()='NBA']");
  if (byText){ await byText.click(); await page.waitForTimeout(600); return true; }
  return false;
}

async function ensureInPicks(page){
  // If on marketing homepage, click Pick Now or Players
  const pickNow = await page.$('xpath=//button[contains(translate(.,"PICK NOW","pick now"),"pick now") or @aria-label="Pick Now"]');
  if (pickNow) { await pickNow.click(); await page.waitForTimeout(1200); }
  const players = await page.$('xpath=//a[contains(translate(.,"PLAYERS","players"),"players")]');
  if (players) { await players.click(); await page.waitForTimeout(1200); }
  // Fallback direct navigation if content still looks like marketing page
  const onMarketing = await page.evaluate(()=>/All your picks\. One app\./i.test(document.body.textContent||''));
  if (onMarketing){ await page.goto('https://www.prizepicks.com/', { waitUntil: 'domcontentloaded' }); }
  // Wait for tabs/chips to render
  for (let i=0;i<10;i++){
    const shellReady = await page.$('[role="tablist"], [data-testid*="chip" i], [data-testid*="players" i]');
    if (shellReady) break;
    await page.waitForTimeout(300);
  }
}

async function findPlayerCard(page, name){
  const target = norm(name);
  const candidates = await page.$$('[data-testid*="player-card"], .PlayerCard, [class*="PlayerCard"]');
  for (const c of candidates){
    const txt = norm(await c.textContent());
    if (txt.includes(target)) return c;
  }
  return null;
}

async function clickPropTab(page, prop){
  const p = norm(prop);
  const tabs = await page.$$('button, [role="tab"], [data-testid*="tab"], [class*="Tab"]');
  for (const t of tabs){
    const txt = norm(await t.textContent());
    if (txt.includes(p)) { await t.click(); await page.waitForTimeout(400); return true; }
  }
  return false;
}

async function chooseSide(card, side){
  const wantOver = String(side||'Over').toLowerCase() === 'over';
  const overCand = await card.$('[data-testid*="over" i], [aria-label*="Over"], button');
  const underCand = await card.$('[data-testid*="under" i], [aria-label*="Under"], button');
  let overBtn = overCand;
  if (overBtn){
    const txt = (await overBtn.textContent()||'');
    if (!/over/i.test(txt)) overBtn = await card.$('xpath=.//button[contains(translate(.,"OVER","over"),"over")]');
  }
  let underBtn = underCand;
  if (underBtn){
    const txt = (await underBtn.textContent()||'');
    if (!/under/i.test(txt)) underBtn = await card.$('xpath=.//button[contains(translate(.,"UNDER","under"),"under")]');
  }
  const clickBtn = wantOver ? (overBtn || overCand) : (underBtn || underCand);
  if (clickBtn) { await clickBtn.click(); await card.page().waitForTimeout(300); return true; }
  await card.click(); await card.page().waitForTimeout(300); return true;
}

async function main(){
  const argv = yargs(hideBin(process.argv))
    .option('slip', { type: 'string', describe: 'Path to slip JSON {items:[{name,prop,side}]}' })
    .option('cgpp', { type: 'string', describe: 'Base64 cgpp hash payload' })
    .option('cgppFile', { type: 'string', describe: 'Path to file containing base64 cgpp payload' })
    .option('headful', { type: 'boolean', default: false, describe: 'Run with UI for debugging' })
    .argv;

  let items = null;
  // Accept cgpp via CLI, file, or environment variable CGPP
  let cgpp = argv.cgpp;
  if (!cgpp && argv.cgppFile && fs.existsSync(argv.cgppFile)){
    try { cgpp = fs.readFileSync(argv.cgppFile, 'utf8').trim(); } catch(e) {}
  }
  if (!cgpp && process.env.CGPP) cgpp = process.env.CGPP.trim();
  if (cgpp) items = decodeCgpp(cgpp);
  if (!items && argv.slip) items = readSlipFromFile(argv.slip);
  const onlyNavigate = !items;

  const browser = await chromium.launch({ headless: !argv.headful });
  const contextOpts = fs.existsSync(STORAGE_PATH) ? { storageState: STORAGE_PATH } : {};
  const context = await browser.newContext(contextOpts);
  // Grant geolocation permission to avoid the location popup blocking interaction
  try{
    await context.grantPermissions(['geolocation'], { origin: 'https://app.prizepicks.com' });
    // Set a default geolocation (approx US city) if needed
    await context.setGeolocation({ latitude: 37.7749, longitude: -122.4194 });
  }catch(e){ /* permissions might not be required; continue */ }
  const page = await context.newPage();

  await page.goto('https://app.prizepicks.com/', { waitUntil: 'load' });
  // Extra sleeps to move past marketing/landing transitions
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
  // Dismiss privacy/cookie banner if present
  try{
    const acceptAll = await page.$("xpath=//button[normalize-space()='Accept All']");
    if (acceptAll){ await acceptAll.click(); await page.waitForTimeout(600); }
  }catch(e){}
  // Close tutorial modal "How to Play" if visible
  try{
    const closeTutorial = await page.$("xpath=//div[contains(.,'How to Play')]/ancestor::div[contains(@role,'dialog')]//button[contains(@aria-label,'Close') or contains(.,'×')]");
    if (closeTutorial){ await closeTutorial.click(); await page.waitForTimeout(600); }
  }catch(e){}
  // Wait for human verification gate (Press & Hold)
  try{
    const humanGate = await page.$("xpath=//div[contains(.,'Before we continue') or contains(.,'Press & Hold')]");
    if (humanGate){
      console.log('[PP-AUTO]', 'Human verification detected. Please press & hold to continue...');
      // Poll until gate disappears (up to 2 minutes)
      const start = Date.now();
      while (Date.now() - start < 120000){
        const stillThere = await page.$("xpath=//div[contains(.,'Before we continue') or contains(.,'Press & Hold')]");
        if (!stillThere) break;
        await page.waitForTimeout(1000);
      }
    }
  }catch(e){}
  // Close any in-page geolocation modal if present
  try{
    const allowBtn = await page.$("xpath=//button[contains(.,'Allow while visiting the site') or contains(.,'Allow this time')]");
    if (allowBtn){ await allowBtn.click(); await page.waitForTimeout(800); }
  }catch(e){ /* ignore */ }
  // Handle occasional 404 "Page Not Found" screen
  try{
    const is404 = await page.evaluate(()=>/Page Not Found/i.test(document.body.textContent||''));
    if (is404){
      const goHomeBtn = await page.$("xpath=//button[normalize-space()='Go Home']");
      if (goHomeBtn) { await goHomeBtn.click(); await page.waitForTimeout(1200); }
      // Direct route to players if still stuck
      const still404 = await page.evaluate(()=>/Page Not Found/i.test(document.body.textContent||''));
      if (still404){
        await page.goto('https://app.prizepicks.com/players', { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(1000);
      }
    }
  }catch(e){/* noop */}
  // Try up to 5 passes to enter picks UI and select NBA
  for (let i=0; i<5; i++){
    await ensureInPicks(page);
    await page.waitForTimeout(1000);
    const selected = await selectNBA(page);
    if (selected) break;
    await page.waitForTimeout(1500);
  }

  if (!onlyNavigate){
    for (const it of items){
    try{
      await clickPropTab(page, it.prop);
      const card = await findPlayerCard(page, it.name);
      if (!card) { console.warn('[PP-AUTO]', 'Player not found:', it.name); continue; }
      await chooseSide(card, it.side || 'Over');
      }catch(e){ console.warn('[PP-AUTO]', 'Failed on item', it, e.message); }
      await page.waitForTimeout(250);
    }
  } else {
    console.log('[PP-AUTO]', 'Navigation only: opened app and selected NBA tab. Provide --cgpp or --slip to autofill picks.');
    await page.waitForTimeout(1000);
  }

  // Keep open briefly if headful for visual confirmation
  if (argv.headful){
    console.log('[PP-AUTO]', 'Complete. Close the window to finish.');
    await page.waitForTimeout(3000);
  }
  await browser.close();
}

main().catch((e)=>{ console.error(e); process.exit(1); });
