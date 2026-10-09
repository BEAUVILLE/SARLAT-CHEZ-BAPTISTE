'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const html=fs.readFileSync(path.resolve(__dirname,'../index.html'),'utf8');
const scriptAt=html.indexOf("const openBtn=document.getElementById('digiyOwnerOpen');");
assert.ok(scriptAt>0,'explicit owner control must exist');
const scriptStart=html.lastIndexOf('(function(){',scriptAt);
const scriptEnd=html.indexOf('})();',scriptAt);
assert.ok(scriptStart>0&&scriptEnd>scriptAt,'owner snippet boundaries');
const code=html.slice(scriptStart,scriptEnd+5);

function sandbox(hash,hasSupabase=true){
  const on=new Map();
  const items={
    digiyOwnerOpen:{addEventListener:(kind,fn)=>on.set('open:'+kind,fn)},
    digiyOwnerOverlay:{hidden:true},
    digiyOwnerFrame:{dataset:{},src:''},
    digiyOwnerClose:{addEventListener:(kind,fn)=>on.set('close:'+kind,fn)},
  };
  const host={
    document:{
      getElementById:id=>items[id],
      documentElement:{style:{overflow:''}}
    },
    location:{hash},
    window:{
      supabase:hasSupabase?{}:undefined,
      addEventListener:(event,fn)=>on.set('window:'+event,fn),
      DIGIY_SYNC_PUBLIC_LOC:()=>{}
    },
    alert:()=>{}
  };
  vm.runInNewContext(code,host,{timeout:1000});
  return {items,host,on};
}
test('public Sarlat URL never automatically displays the private owner overlay',()=>{
  for(const fragment of ['', '#owner','#reservation','#gallery','#info','#contact']){
    const {items,on}=sandbox(fragment);
    assert.equal(items.digiyOwnerOverlay.hidden,true,fragment);
    assert.equal(items.digiyOwnerFrame.src,'',fragment);
    assert.equal(items.digiyOwnerFrame.dataset.loaded,undefined,fragment);
    assert.equal(on.has('window:hashchange'),false,'hash is not a privileged intent');
  }
});
test('owner overlay opens only on dedicated explicit owner button click',()=>{
  const {items,on}=sandbox('');
  const handler=on.get('open:click');
  assert.equal(typeof handler,'function');
  let prevented=false;
  handler({preventDefault:()=>{prevented=true}});
  assert.equal(prevented,true);
  assert.equal(items.digiyOwnerOverlay.hidden,false);
  assert.equal(items.digiyOwnerFrame.src,'/gestion.html?v=20261002-owner-single-source-v1');
  assert.equal(items.digiyOwnerFrame.dataset.loaded,'1');
});
test('closing owner overlay restores public access without redirect',()=>{
  const {items,on,host}=sandbox('#reservation');
  on.get('open:click')({preventDefault:()=>{}});
  on.get('close:click')();
  assert.equal(items.digiyOwnerOverlay.hidden,true);
  assert.equal(host.document.documentElement.style.overflow,'');
  assert.equal(host.location.hash,'#reservation');
});
test('public reservation, contact and photo entrypoints are still public',()=>{
  assert.match(html,/<a[^>]+href="#reservation"[^>]*>Faire une demande directe/);
  assert.match(html,/href="#gallery"[^>]*data-mobile-target="gallery"/);
  assert.match(html,/href="#contact"[^>]*data-mobile-target="contact"/);
  assert.match(html,/href="https:\/\/sarlat-chez-baptiste\.digiylyfe\.com\/"[^>]*rel="noopener"/);
  assert.doesNotMatch(html,/location\.hash\s*===?\s*['"]#owner['"]\s*\)\s*(?:setTimeout|openOwner)/);
});
