const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const STORAGE_PATH = path.resolve(__dirname, 'storage-state.json');

async function main(){
  if (fs.existsSync(STORAGE_PATH)){
    console.log('[PP-AUTO]', 'Storage state already exists at', STORAGE_PATH);
    console.log('[PP-AUTO]', 'If you need to relogin, delete this file and rerun.');
  }

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();
  console.log('[PP-AUTO]', 'Opening PrizePicks login...');
  await page.goto('https://www.prizepicks.com/login', { waitUntil: 'load' });

  // Helper: detect logged-in by presence of avatar/menu or lack of Login button
  async function isLoggedIn(){
    try{
      return await page.evaluate(()=>{
        const hasAvatar = !!document.querySelector('[aria-label*="account" i], [data-testid*="avatar" i], [class*="Avatar" i]');
        const loginBtn = Array.from(document.querySelectorAll('a,button')).find(el=>/log\s*in/i.test(el.textContent||''));
        return hasAvatar || !loginBtn;
      });
    }catch{ return false; }
  }

  console.log('[PP-AUTO]', 'Please complete login in the opened window.');
  console.log('[PP-AUTO]', 'This will save a session for re-use.');

  // Poll for login success up to ~3 minutes
  const start = Date.now();
  while (Date.now() - start < 180000){
    if (await isLoggedIn()){
      console.log('[PP-AUTO]', 'Login detected. Saving session...');
      await context.storageState({ path: STORAGE_PATH });
      console.log('[PP-AUTO]', 'Session saved to', STORAGE_PATH);
      await browser.close();
      process.exit(0);
    }
    await page.waitForTimeout(1500);
  }

  console.warn('[PP-AUTO]', 'Timed out waiting for login. You can keep the window open and rerun.');
  try{ await context.storageState({ path: STORAGE_PATH }); }catch{}
  await browser.close();
}

main().catch(async (e)=>{ console.error(e); process.exit(1); });
