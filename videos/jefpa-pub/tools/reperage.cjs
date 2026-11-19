// Repérage : parcourt chaque page en défilant doucement (horloge contrôlée) et prend une image tous les ~600 px.
const {chromium}=require('playwright');
const pages=process.argv.slice(3), out=process.argv[2];
(async()=>{
  const b=await chromium.launch();
  for(const u of pages){
    const ctx=await b.newContext({viewport:{width:1440,height:810},deviceScaleFactor:1});
    const p=await ctx.newPage();
    await p.clock.install({time:new Date('2026-11-13T10:00:00')});
    await p.goto('https://jefpa-site.pages.dev'+u,{waitUntil:'networkidle',timeout:60000});
    for(let i=0;i<20;i++)await p.clock.runFor(100);
    const h=await p.evaluate(()=>document.documentElement.scrollHeight);
    const nom=u.replace(/[\/.]/g,'_')||'accueil';
    let y=0,k=0;
    await p.screenshot({path:`${out}/${nom}-${String(k++).padStart(2,'0')}.jpg`,type:'jpeg',quality:70});
    while(y<h-810){
      for(let s=0;s<10;s++){y+=60;await p.evaluate(y=>scrollTo(0,y),y);await p.clock.runFor(50);}
      await p.clock.runFor(400);
      await p.screenshot({path:`${out}/${nom}-${String(k++).padStart(2,'0')}.jpg`,type:'jpeg',quality:70});
    }
    console.log(nom,h,k);
    await ctx.close();
  }
  await b.close();})();
