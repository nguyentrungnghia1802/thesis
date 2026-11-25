
const {chromium} = require(process.env.THESIS_PLAYWRIGHT);
const fs = require('node:fs/promises');
const path = require('node:path');
async function main() {
  const [port, folder, player, role, group] = process.argv.slice(2);
  const origin = 'http://127.0.0.1:' + Number(port);
  const browser = await chromium.launch({
    executablePath: String.raw`C:\Program Files\Google\Chrome\Application\chrome.exe`,
    headless: true,
    args: ['--disable-background-networking', '--no-first-run']
  });
  try {
    const page = await browser.newPage({viewport:{width:900,height:760},deviceScaleFactor:2});
    await page.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.origin === origin || url.protocol === 'data:') await route.continue();
      else await route.abort();
    });
    await page.goto(origin + '/oe',{waitUntil:'domcontentloaded',timeout:7000});
    const index = await page.content();
    await fs.writeFile(path.join(folder,'moise-index.html'),index);
    const links = await page.locator('a[href]').evaluateAll((anchors) =>
      anchors.map(a=>({text:a.textContent.trim(),href:a.getAttribute('href')}))
    );
    console.log('Moise links:', JSON.stringify(links));
    const target = links.find(l => l.text === group) ||
                   links.find(l => new RegExp('(^|[/_-])'+group+'(?:[/?#]|$)').test(l.href)) ||
                   links.find(l => l.text.includes(group) && l.href.startsWith('/'));
    if (!target) throw new Error('No native group link for '+group);
    const url = new URL(target.href,origin);
    if (url.hostname !== '127.0.0.1' && url.hostname !== 'localhost') url.hostname='127.0.0.1';
    if (url.origin !== origin) throw new Error('Group link is outside the live producer');
    await page.goto(url.href,{waitUntil:'domcontentloaded',timeout:7000});
    const body = await page.locator('body').innerText();
    await fs.writeFile(path.join(folder,'moise-group.html'),await page.content());
    await fs.writeFile(path.join(folder,'moise-group.txt'),body);
    for (const label of [player,role,group]) {
      if (!body.includes(label)) throw new Error('Missing in live Moise view: '+label);
    }
    await page.screenshot({path:path.join(folder,'moise-group-original.png'),fullPage:true,timeout:8000});
    const boxes = await page.evaluate(labels => {
      const picker=(predicate) => Array.from(document.querySelectorAll('th,td,b,strong,h1,h2,h3,h4,span,a,p'))
        .filter(x=>predicate(x.innerText.trim()) &&
          x.getBoundingClientRect().width>0 && x.getBoundingClientRect().height>0)
        .map(x=>{const r=x.getBoundingClientRect();return {text:x.innerText.trim(),x:r.x,y:r.y,width:r.width,height:r.height,tag:x.tagName,
          row:x.closest('tr')?.innerText};});
      return Object.fromEntries(labels.map(k=>[k,picker(text=>text===k||text.includes(k)&&text.length<95)]));
    },[player,role,group]);
    await fs.writeFile(path.join(folder,'moise-boxes.json'),JSON.stringify({url:url.href,scale:2,boxes},null,2));
    console.log('Live Moise group view captured '+url.pathname);
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error);process.exitCode=1; });

