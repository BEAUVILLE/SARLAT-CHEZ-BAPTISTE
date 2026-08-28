/* SARLAT CHEZ BAPTISTE · i18n public V1 · FR EN ES PT IT DE NL AR */
(function(){
'use strict';
var LANGS=['fr','en','es','pt','it','de','nl','ar'];
var Q=new URLSearchParams(location.search),requested=(Q.get('lang')||'').slice(0,2).toLowerCase(),stored='';
try{stored=(localStorage.getItem('digiy-lang')||'').slice(0,2).toLowerCase()}catch(e){}
var lang=LANGS.indexOf(requested)>=0?requested:(LANGS.indexOf(stored)>=0?stored:'fr');
var locale={fr:'fr-FR',en:'en-GB',es:'es-ES',pt:'pt-PT',it:'it-IT',de:'de-DE',nl:'nl-NL',ar:'ar'}[lang]||'fr-FR';
var frMonths=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];
function $(s,r){return (r||document).querySelector(s)}
function $$(s,r){return Array.from((r||document).querySelectorAll(s))}
function text(el,v){if(el&&typeof v==='string'&&el.textContent!==v)el.textContent=v}
function attr(el,k,v){if(el&&typeof v==='string')el.setAttribute(k,v)}
function fmtMonth(y,m){return new Intl.DateTimeFormat(locale,{month:'long',year:'numeric'}).format(new Date(y,m,1))}
function replaceFrenchMonths(s){
  var out=String(s||'');
  frMonths.forEach(function(m,i){
    var re=new RegExp(m,'gi');
    if(re.test(out)){
      var local=new Intl.DateTimeFormat(locale,{month:'long'}).format(new Date(2026,i,1));
      out=out.replace(new RegExp(m,'gi'),local);
    }
  });
  return out;
}
function translateDatePhrase(s,tr){
  var out=replaceFrenchMonths(s);
  if(lang!=='fr') out=out.replace(/\sau\s/g,tr.rangeTo||' – ').replace(/\set\s/g,tr.and||' and ');
  return out;
}
function makeBar(){
  var top=$('.top');if(!top||$('.sarlat-langs'))return;
  var style=document.createElement('style');style.textContent='.sarlat-langs{display:flex;gap:4px;flex-wrap:wrap;justify-content:center;align-items:center}.sarlat-langs button{min-width:34px;height:32px;border:1px solid rgba(65,43,25,.22);border-radius:999px;background:#fff9;color:#25190f;font-size:10px;font-weight:1000;cursor:pointer}.sarlat-langs button.active{background:#315b43;color:#fff;border-color:#315b43}@media(max-width:600px){.top{row-gap:6px}.top-actions{order:2}.sarlat-langs{order:3;width:100%;justify-content:flex-start;overflow:visible;flex-wrap:nowrap;padding:2px 0 0;position:relative;z-index:2}.sarlat-langs button{min-width:30px;width:30px;height:28px;font-size:9px}.top-actions>a:first-child{min-height:30px!important;padding:5px 8px!important;font-size:9px!important;border-width:1px!important;gap:4px!important;justify-self:start!important;transform:translateX(-4px);white-space:nowrap}}';document.head.appendChild(style);
  var bar=document.createElement('div');bar.className='sarlat-langs';bar.setAttribute('aria-label','Languages');
  LANGS.forEach(function(l){var b=document.createElement('button');b.type='button';b.textContent=l.toUpperCase();b.classList.toggle('active',l===lang);b.addEventListener('click',function(){try{localStorage.setItem('digiy-lang',l)}catch(e){}var u=new URL(location.href);u.searchParams.set('lang',l);location.href=u.pathname+u.search+u.hash});bar.appendChild(b)});
  var actions=$('.top-actions');top.insertBefore(bar,actions||null);
}
function applyStatic(tr){
  document.documentElement.lang=lang;document.documentElement.dir=lang==='ar'?'rtl':'ltr';
  document.title=tr.title||document.title;var md=$('meta[name="description"]');if(md)md.content=tr.desc||md.content;
  text($('.brand small'),tr.brandSub);
  var ta=$$('.top-actions a');text(ta[0],tr.returnDigiy);text(ta[1],tr.discoverSarlat);text(ta[2],tr.owner);
  text($('.hero-badge'),tr.heroBadge);text($('.hero .tagline'),tr.tagline);text($('.price-block-hero strong'),tr.priceNight);
  var ha=$$('.hero .actions a');text(ha[0],tr.directRequest);text(ha[1],tr.writeWhatsapp);
  $$('.cards .card').forEach(function(c,i){if(!tr.cards||!tr.cards[i])return;text($('b',c),tr.cards[i][0]);text($('small',c),tr.cards[i][1])});
  var info=$('#info');if(info){info.dataset.mobileAccordion=tr.infoAccordion;text($('.eyebrow',info),tr.infoEyebrow);text($('h2',info),tr.infoTitle);var box=$('.box',info);text($('h3',box),tr.privateTitle);text($('p',box),tr.privateText);$$('.list .item',info).forEach(function(e,i){text(e,tr.amenities&&tr.amenities[i])})}
  var gal=$('#gallery');if(gal){gal.dataset.mobileAccordion=tr.galleryAccordion;text($('.eyebrow',gal),tr.photosReal);text($('h2',gal),tr.spaces)}
  var res=$('#reservation');if(res){text($('.eyebrow',res),tr.reservationEyebrow);text($('h2',res),tr.chooseDates);text($('.intro',res),tr.reservationIntro)}
  var dr=$('#dateRange');if(dr&&/Sélectionnez vos dates/.test(dr.textContent))text(dr,'📅 '+tr.selectDates);
  var legend=$$('.calendar-legend > span');[tr.available,tr.occupied,tr.closed,tr.selected].forEach(function(v,i){if(legend[i]){var dot=$('.dot',legend[i]);legend[i].innerHTML='';if(dot)legend[i].appendChild(dot);legend[i].appendChild(document.createTextNode(' '+v))}});
  var labels=tr.labels||{};Object.keys(labels).forEach(function(id){text($('label[for="'+id+'"]'),labels[id])});
  var opts=$$('#guests option');text(opts[0],tr.guest1);text(opts[1],tr.guest2);
  var est=$('#estimate');if(est){text($('strong',est),tr.priceNight);text($('span',est),tr.estimateHint)}
  text($('.note',res),tr.formNote);text($('#requestForm button[type="submit"]'),tr.submitWa);text($('#emailRequest'),tr.sendEmail);
  var sum=$('.summary');if(sum){text($('h3',sum),tr.before);$$('li',sum).forEach(function(e,i){text(e,tr.summary&&tr.summary[i])})}
  var contact=$('#contact');if(contact){contact.dataset.mobileAccordion=tr.contactAccordion;text($('.eyebrow',contact),tr.contactEyebrow);text($('h2',contact),tr.contactTitle);var links=$$('.list .item',contact);text(links[0],tr.whatsappFrance);text(links[1],tr.emailLabel);var pay=$('.payment',contact);text($('h3',pay),tr.paymentTitle);text($('.country-label',pay),tr.country);var ps=$$('p',pay);if(ps[1])text(ps[1],tr.beneficiary);if(ps[2])ps[2].innerHTML=tr.verifyPayment;text($('#copyPay'),tr.copyNumber)}
  var off=$('#official');if(off){off.dataset.mobileAccordion=tr.officialAccordion;text($('.eyebrow',off),tr.officialEyebrow);text($('h2',off),tr.officialTitle);text($('.intro',off),tr.officialIntro);var oa=$$('.actions a',off);text(oa[0],tr.chooseDatesBtn);text(oa[1],tr.writeBaptiste);text(oa[2],tr.sendEmailBtn);text(oa[3],tr.seeAddress);var bs=$$('.official-card b',off),ss=$$('.official-card small',off);text(bs[0],tr.cardRoom);text(ss[0],tr.cardReturn);text(ss[1],tr.ecosystem)}
  var nav=$('.mobile-quick-nav');if(nav){attr(nav,'aria-label',tr.quickNavAria);$$('a span',nav).forEach(function(e,i){text(e,tr.nav&&tr.nav[i])})}
  var footer=$('.footer');if(footer){footer.innerHTML='<strong>DIGIYLYFE ∞ SARLAT CHEZ BAPTISTE</strong><br>'+tr.footer+'<div style="margin-top:12px;line-height:1.5;"><strong>DIGIYLYFE</strong><br><strong>LE SAVOIR-FAIRE POUR LE SAVOIR-ÊTRE.</strong></div>'}
  var wa='https://wa.me/33638329423?text='+encodeURIComponent(tr.waIntro);['waTop','waDirect','waBottom'].forEach(function(id){var e=$('#'+id);if(e)e.href=wa});
  applyGenerated(tr);makeBar();
}
function applyGenerated(tr){
  var days=$$('.calendar-grid .day-name');if(days.length)days.forEach(function(e,i){text(e,tr.weekdays&&tr.weekdays[i])});
  var my=$('#monthYear');if(my&&lang!=='fr'){
    var raw=my.textContent.toLowerCase(),mi=-1;frMonths.some(function(m,i){if(raw.indexOf(m)>=0){mi=i;return true}return false});var ym=raw.match(/(20\d{2})/);if(mi>=0&&ym)text(my,fmtMonth(Number(ym[1]),mi));
  }
  var dr=$('#dateRange');if(dr){if(/Sélectionnez vos dates/.test(dr.textContent))text(dr,'📅 '+tr.selectDates);else if(lang!=='fr')text(dr,translateDatePhrase(dr.textContent,tr))}
  var nd=$('#nightsDisplay');if(nd){var m=nd.textContent.match(/(\d+)\s+nuit(?:s)?/i);if(m)text(nd,'🛏️ '+m[1]+' '+(Number(m[1])===1?tr.night:tr.nights))}
  var est=$('#estimate');if(est){var st=$('strong',est),sp=$('span',est);if(st){var m2=st.textContent.match(/(\d+)\s+nuitée\(s\)\s*:\s*(.+)/i);if(m2)text(st,m2[1]+' '+(Number(m2[1])===1?tr.nightStay:tr.nightStays)+' : '+m2[2]);else if(/78\s*€\s*\/\s*nuitée/i.test(st.textContent))text(st,tr.priceNight)}if(sp){if(/^Estimation\s*:/i.test(sp.textContent))text(sp,sp.textContent.replace(/^Estimation/i,tr.estimateLabel));else if(/choisissez vos dates/i.test(sp.textContent))text(sp,tr.estimateHint)}}
  $$('#availabilityList .period').forEach(function(row){var s=$('span',row),b=$('strong',row);if(s){var v=s.textContent;if(/Autres dates jusqu'au 30 octobre 2026/i.test(v))v=tr.otherDates;else if(/À partir du 31 octobre 2026/i.test(v))v=tr.fromOct31;else if(lang!=='fr')v=translateDatePhrase(v,tr);text(s,v)}if(b){var bv=b.textContent.trim();if(bv==='Occupé')text(b,tr.occupied);else if(bv==='Fermé')text(b,tr.closed);else if(bv==='Sur demande')text(b,tr.onRequest)}});
  $$('.slide-caption').forEach(function(e,i){if(tr.slideCaptions&&tr.slideCaptions[i])text(e,tr.slideCaptions[i])});
  var promo=$('.promo-copy');if(promo){text($('.promo-kicker',promo),tr.promoKicker);text($('p',promo),tr.promoText);var pa=$('.promo-actions a',promo),pb=$('.promo-share-btn',promo);text(pa,tr.promoOpen);text(pb,tr.promoShare);$$('.promo-qr-item small').forEach(function(e){text(e,tr.qrAccess)})}
  $$('[data-mobile-accordion]').forEach(function(sec){var btn=$(':scope > .mobile-section-toggle strong',sec);if(btn)text(btn,sec.dataset.mobileAccordion)});
}
function translatedRequest(tr){
  var form=$('#requestForm'),a=$('#arrival'),d=$('#departure');if(!form)return null;var f=new FormData(form),av=a?a.value:f.get('arrival'),dv=d?d.value:f.get('departure');if(!av||!dv)throw new Error(tr.formErrorDates);var n=Math.round((new Date(dv+'T12:00')-new Date(av+'T12:00'))/86400000);if(n<=0)throw new Error(tr.formErrorDeparture);var guests=f.get('guests')||'2',name=f.get('name')||tr.noneName,contact=f.get('contact')||tr.noneContact,time=f.get('time')||tr.timeDefault,msg=f.get('message')||tr.noExtra;return [tr.hello,'',tr.requestIntro,tr.arrival+' : '+av,tr.departure+' : '+dv,tr.guests+' : '+guests,tr.name+' : '+name,tr.contact+' : '+contact,tr.arrivalTime+' : '+time,tr.estimateLabel+' : '+(n*78).toLocaleString(locale)+' € / '+(n*51165).toLocaleString(locale)+' FCFA',tr.paymentAfter,tr.message+' : '+msg,'',tr.understand].join('\n')}
function bindInteractions(tr){
  var form=$('#requestForm');if(form)form.addEventListener('submit',function(e){e.preventDefault();e.stopImmediatePropagation();var st=$('#status');if(st)st.textContent='';try{var msg=translatedRequest(tr);window.open('https://wa.me/33638329423?text='+encodeURIComponent(msg),'_blank','noopener');text(st,tr.waReady)}catch(err){text(st,'⚠️ '+err.message)}},true);
  var em=$('#emailRequest');if(em)em.addEventListener('click',function(e){e.preventDefault();e.stopImmediatePropagation();var st=$('#status');if(st)st.textContent='';try{var msg=translatedRequest(tr);location.href='mailto:baptistejb24@gmail.com?subject='+encodeURIComponent(tr.emailSubject)+'&body='+encodeURIComponent(msg)}catch(err){text(st,'⚠️ '+err.message)}},true);
  var cp=$('#copyPay');if(cp)cp.addEventListener('click',function(e){e.preventDefault();e.stopImmediatePropagation();var out=$('#copyStatus'),num='+221 77 134 28 89';if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText('+221771342889').then(function(){text(out,tr.copied+num+' ('+(lang==='fr'?'Sénégal':'Senegal')+')')}).catch(function(){text(out,'📋 '+num)})}else text(out,'📋 '+num)},true);
  document.addEventListener('click',function(e){var b=e.target.closest('.promo-share-btn');if(!b)return;e.preventDefault();e.stopImmediatePropagation();var status=$('.promo-share-status',b.closest('.promo-copy')),data={title:'SARLAT CHEZ BAPTISTE',text:tr.shareText,url:'https://sarlat-chez-baptiste.digiylyfe.com/?lang='+lang};(async function(){try{if(navigator.share){await navigator.share(data);text(status,tr.shareReady)}else if(navigator.clipboard){await navigator.clipboard.writeText(data.url);text(status,tr.linkCopied)}else text(status,data.url)}catch(err){if(!err||err.name!=='AbortError')text(status,tr.copyLink+data.url)}})()},true);
}
function watch(tr){var timer=0,obs=new MutationObserver(function(){clearTimeout(timer);timer=setTimeout(function(){applyGenerated(tr)},20)});['calendarGrid','monthYear','availabilityList','dateRange','nightsDisplay','estimate','sliderTrack'].forEach(function(id){var e=$('#'+id);if(e)obs.observe(e,{childList:true,subtree:true,characterData:true})})}
function start(){
  var s=document.createElement('script');s.src='i18n/'+lang+'.js?v=20260828-i18n-v1';s.onload=function(){var tr=window.DIGIY_SARLAT_LANG;if(!tr)return;try{localStorage.setItem('digiy-lang',lang)}catch(e){}applyStatic(tr);bindInteractions(tr);watch(tr)};s.onerror=function(){if(lang!=='fr'){var u=new URL(location.href);u.searchParams.set('lang','fr');location.replace(u.href)}};document.head.appendChild(s);
}
start();
})();
