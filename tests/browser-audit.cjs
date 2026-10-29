// Uses the browser runtime bundled with Codex; all page content is synthetic.
const { chromium } = require('C:/Users/Lenovo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
  const browser = await chromium.launch({headless:true, executablePath:process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const page = await browser.newPage();
  const results=[];
  const axePath=process.env.AXE_SCRIPT_PATH;
  let axeVersion=null;
  for (const state of ['ready','empty','unavailable','partial']) {
    const suffix=state==='partial'?'skills=unavailable&academic=ready':`state=${state}`;
    for (const viewport of [{width:1280,height:900},{width:320,height:760},{width:760,height:320}]) {
      await page.setViewportSize(viewport);
      await page.goto(`http://127.0.0.1:5051/?${suffix}`);
      await page.emulateMedia({reducedMotion:'reduce'});
      await page.keyboard.press('Tab');
      const skip=await page.evaluate(()=>document.activeElement.textContent.trim());
      await page.keyboard.press('Enter');
      const target=await page.evaluate(()=>document.activeElement.id);
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
      await page.addStyleTag({content:'html {font-size:200%} p,li {line-height:1.5;letter-spacing:.12em;word-spacing:.16em} p {margin-bottom:2em}'});
      const enlargedOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
      let violations=null;
      if (axePath) {
        await page.addScriptTag({path:axePath});
        axeVersion=await page.evaluate(()=>axe.version);
        violations=(await page.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}))).violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}));
      }
      results.push({state,viewport,skip,target,overflow,enlargedOverflow,violations});
      if (overflow || enlargedOverflow || target!=='contenido' || violations?.length) throw new Error(JSON.stringify(results.at(-1)));
    }
  }
  await page.setViewportSize({width:1280,height:900});
  await page.goto('http://127.0.0.1:5051/');
  fs.mkdirSync('specs/001-perfil-publico/evidence',{recursive:true});
  await page.screenshot({path:'specs/001-perfil-publico/evidence/desktop.png',fullPage:true});
  await page.setViewportSize({width:320,height:760});
  await page.screenshot({path:'specs/001-perfil-publico/evidence/mobile.png',fullPage:true});
  const noJS=await browser.newContext({javaScriptEnabled:false});
  const plain=await noJS.newPage();
  await plain.goto('http://127.0.0.1:5051/');
  if (!(await plain.locator('h1').textContent()).includes('sintética')) throw new Error('No-JS content missing');
  fs.writeFileSync('specs/001-perfil-publico/evidence/browser-audit.json',JSON.stringify({browserVersion:browser.version(),axeVersion,results,noJavaScript:true},null,2));
  await browser.close();
  console.log(`${results.length} browser scenarios passed; no-JS passed; axe ${axePath?'enabled':'pending'}`);
})().catch(error=>{console.error(error);process.exit(1)});
