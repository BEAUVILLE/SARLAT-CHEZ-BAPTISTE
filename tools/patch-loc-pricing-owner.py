from pathlib import Path

path = Path('gestion.html')
html = path.read_text(encoding='utf-8')

if 'id="basePrice"' in html:
    print('Tarification propriétaire déjà présente.')
    raise SystemExit(0)

css_anchor = '@media(max-width:560px){.state-actions{grid-template-columns:1fr}'
css_extra = '.pricing{margin-top:14px;padding:14px;border:1px solid #d8c8b6;border-radius:18px;background:#fffaf1}.pricing-title{font-weight:1000;font-size:15px}.pricing-note{margin-top:5px;color:#6e5845;font-size:12px;font-weight:750;line-height:1.45}.price-grid{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:end}.price-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.price-current{margin-top:8px;font-size:12px;font-weight:950;color:#315b43}.day{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;line-height:1}.day .day-price{font-size:9px;font-weight:1000;opacity:.82;white-space:nowrap}@media(max-width:560px){.price-grid{grid-template-columns:1fr}.state-actions{grid-template-columns:1fr}'
if css_anchor not in html:
    raise SystemExit('Ancre CSS introuvable')
html = html.replace(css_anchor, css_extra, 1)

html = html.replace(
    'Connectez-vous pour ouvrir, occuper ou fermer des dates.',
    'Connectez-vous pour ouvrir, occuper ou fermer des dates, et régler vos tarifs.',
    1,
)
html = html.replace(
    'Cliquez une date pour la sélectionner. Cliquez une seconde date pour sélectionner toute la période. Puis choisissez son état.',
    'Cliquez une date pour agir jour par jour, ou une seconde date pour sélectionner toute une période. Vous pouvez ensuite changer son état ou son tarif.',
    1,
)

unit_block = '''    <div class="field hidden" id="unitField">
      <label for="unitSelect">Hébergement / chambre</label>
      <select id="unitSelect"></select>
    </div>'''
base_block = unit_block + '''

    <div class="pricing" id="basePricing">
      <div class="pricing-title">💶 Tarif de base</div>
      <p class="pricing-note">Ce tarif s'applique automatiquement à toutes les nuits sans prix spécial.</p>
      <div class="price-grid">
        <div class="field" style="margin-top:8px">
          <label for="basePrice">Tarif de base / nuitée</label>
          <input id="basePrice" type="number" min="0" step="0.01" inputmode="decimal" placeholder="78">
        </div>
        <button class="btn dark" id="saveBasePrice" type="button">Enregistrer le tarif de base</button>
      </div>
      <div class="price-current" id="basePriceInfo"></div>
    </div>'''
if unit_block not in html:
    raise SystemExit('Bloc unitField introuvable')
html = html.replace(unit_block, base_block, 1)

state_block = '''    <div class="state-actions">
      <button class="freeBtn" id="makeAvailable" type="button">🟢 Disponible</button>
      <button class="occBtn" id="makeOccupied" type="button">🔴 Occupé</button>
      <button class="closeBtn" id="makeClosed" type="button">⚫ Fermé</button>
    </div>'''
special_block = state_block + '''

    <div class="pricing" id="specialPricing">
      <div class="pricing-title">🏷️ Prix de la sélection</div>
      <p class="pricing-note"><strong>1 date</strong> = prix de ce jour · <strong>plusieurs dates</strong> = même prix sur toute la période.</p>
      <div class="price-grid">
        <div class="field" style="margin-top:8px">
          <label for="specialPrice">Prix spécial / nuitée</label>
          <input id="specialPrice" type="number" min="0" step="0.01" inputmode="decimal" placeholder="Ex. 95">
        </div>
        <button class="btn primary" id="applySpecialPrice" type="button">Appliquer ce prix</button>
      </div>
      <div class="price-actions">
        <button class="btn ghost" id="clearSpecialPrice" type="button">↩ Revenir au tarif de base</button>
      </div>
      <p class="pricing-note">Priorité : <strong>prix du jour / période → tarif de base</strong>.</p>
    </div>'''
if state_block not in html:
    raise SystemExit('Bloc state-actions introuvable')
html = html.replace(state_block, special_block, 1)

html = html.replace(
    'let siteId=null, units=[], unitId=null, current=new Date(), states=new Map(), start=null, end=null;',
    "let siteId=null, units=[], unitId=null, current=new Date(), states=new Map(), prices=new Map(), basePrice=78, currency='EUR', start=null, end=null;",
    1,
)

needle = "  const selectedDates = () => start ? between(start,end||start) : [];"
replacement = needle + '''
  const money = value => { const n=Number(value); return Number.isFinite(n) ? n.toLocaleString('fr-FR',{maximumFractionDigits:2})+' '+(currency==='EUR'?'€':currency) : '—'; };
  function currentUnit(){return units.find(unit=>unit.id===unitId)||null;}
  function syncBasePrice(){
    const unit=currentUnit();
    basePrice=Number(unit&&unit.base_price!=null?unit.base_price:78);
    currency=(unit&&unit.price_currency)||'EUR';
    $('basePrice').value=Number.isFinite(basePrice)?basePrice:'';
    $('basePriceInfo').textContent='Tarif de base actuel : '+money(basePrice);
  }'''
if needle not in html:
    raise SystemExit('Ancre selectedDates introuvable')
html = html.replace(needle, replacement, 1)

html = html.replace(
    ".select('id,slug,display_name,unit_type,sort_order')",
    ".select('id,slug,display_name,unit_type,sort_order,base_price,price_currency')",
    1,
)
html = html.replace(
    "    $('unitField').classList.toggle('hidden',units.length<2);",
    "    $('unitField').classList.toggle('hidden',units.length<2);\n    syncBasePrice();",
    1,
)

old_load = '''  async function loadStates(){
    if(!unitId)return;
    const from=iso(new Date(today().getFullYear(),today().getMonth(),1,12));
    const {data,error}=await db.from('digiy_loc_master_unit_calendar').select('day,status').eq('unit_id',unitId).gte('day',from).order('day');
    if(error){setMsg(saveStatus,'⚠️ Lecture calendrier impossible : '+error.message,true);return;}
    states=new Map((data||[]).map(r=>[r.day,r.status]));
  }'''
new_load = '''  async function loadStates(){
    if(!unitId)return;
    const from=iso(new Date(today().getFullYear(),today().getMonth(),1,12));
    const {data,error}=await db.from('digiy_loc_master_unit_calendar').select('day,status,price_override').eq('unit_id',unitId).gte('day',from).order('day');
    if(error){setMsg(saveStatus,'⚠️ Lecture calendrier impossible : '+error.message,true);return;}
    states=new Map((data||[]).map(r=>[r.day,r.status]));
    prices=new Map((data||[]).filter(r=>r.price_override!=null).map(r=>[r.day,Number(r.price_override)]));
  }'''
if old_load not in html:
    raise SystemExit('loadStates introuvable')
html = html.replace(old_load, new_load, 1)

old_day = "      b.type='button';b.className='day';b.textContent=d;b.dataset.date=key;"
new_day = "      b.type='button';b.className='day';b.dataset.date=key;const shownPrice=prices.has(key)?prices.get(key):basePrice;b.innerHTML='<span>'+d+'</span><small class=\"day-price\">'+money(shownPrice)+'</small>';"
if old_day not in html:
    raise SystemExit('Rendu jour introuvable')
html = html.replace(old_day, new_day, 1)

start = html.find('  async function applyState(status){')
end = html.find("  $('sendCode').addEventListener", start)
if start < 0 or end < 0:
    raise SystemExit('Bloc applyState introuvable')

new_functions = '''  async function applyState(status){
    const dates=selectedDates(); if(!dates.length)return setMsg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
    if(!unitId)return setMsg(saveStatus,'⚠️ Aucun hébergement sélectionné.',true);
    setMsg(saveStatus,'Enregistrement…');
    const rows=dates.map(day=>({unit_id:unitId,day,status,price_override:prices.has(day)?prices.get(day):null,updated_at:new Date().toISOString()}));
    const {error}=await db.from('digiy_loc_master_unit_calendar').upsert(rows,{onConflict:'unit_id,day'});
    if(error)return setMsg(saveStatus,'⚠️ Enregistrement refusé : '+error.message,true);
    await loadStates(); resetSelection(); render();
    setMsg(saveStatus,'✓ Calendrier enregistré.');
  }

  async function saveBasePrice(){
    const value=Number($('basePrice').value);
    if(!Number.isFinite(value)||value<0)return setMsg(saveStatus,'⚠️ Indiquez un tarif de base valide.',true);
    if(!unitId)return setMsg(saveStatus,'⚠️ Aucun hébergement sélectionné.',true);
    setMsg(saveStatus,'Enregistrement du tarif de base…');
    const {error}=await db.from('digiy_loc_master_units').update({base_price:value,price_currency:currency||'EUR'}).eq('id',unitId);
    if(error)return setMsg(saveStatus,'⚠️ Tarif de base refusé : '+error.message,true);
    const unit=currentUnit(); if(unit){unit.base_price=value;unit.price_currency=currency||'EUR';}
    basePrice=value; syncBasePrice(); render();
    setMsg(saveStatus,'✓ Tarif de base enregistré : '+money(value)+'.');
  }

  async function applySpecialPrice(){
    const dates=selectedDates(); if(!dates.length)return setMsg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
    const value=Number($('specialPrice').value);
    if(!Number.isFinite(value)||value<0)return setMsg(saveStatus,'⚠️ Indiquez un prix spécial valide.',true);
    setMsg(saveStatus,'Enregistrement du prix…');
    const rows=dates.map(day=>({unit_id:unitId,day,status:states.get(day)||'available',price_override:value,updated_at:new Date().toISOString()}));
    const {error}=await db.from('digiy_loc_master_unit_calendar').upsert(rows,{onConflict:'unit_id,day'});
    if(error)return setMsg(saveStatus,'⚠️ Prix refusé : '+error.message,true);
    await loadStates(); render();
    setMsg(saveStatus,'✓ Prix '+money(value)+' appliqué à '+dates.length+(dates.length===1?' journée.':' journées.'));
  }

  async function clearSpecialPrice(){
    const dates=selectedDates(); if(!dates.length)return setMsg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
    setMsg(saveStatus,'Retour au tarif de base…');
    const rows=dates.map(day=>({unit_id:unitId,day,status:states.get(day)||'available',price_override:null,updated_at:new Date().toISOString()}));
    const {error}=await db.from('digiy_loc_master_unit_calendar').upsert(rows,{onConflict:'unit_id,day'});
    if(error)return setMsg(saveStatus,'⚠️ Retour au tarif de base refusé : '+error.message,true);
    await loadStates(); render();
    setMsg(saveStatus,'✓ Tarif de base rétabli sur la sélection.');
  }

'''
html = html[:start] + new_functions + html[end:]

html = html.replace(
    "  $('unitSelect').addEventListener('change',async event=>{unitId=event.target.value;states.clear();resetSelection();setMsg(saveStatus,'');await loadStates();render();});",
    "  $('unitSelect').addEventListener('change',async event=>{unitId=event.target.value;states.clear();prices.clear();resetSelection();setMsg(saveStatus,'');syncBasePrice();await loadStates();render();});",
    1,
)
html = html.replace(
    "  $('makeClosed').addEventListener('click',()=>applyState('closed'));",
    "  $('makeClosed').addEventListener('click',()=>applyState('closed'));\n  $('saveBasePrice').addEventListener('click',saveBasePrice);\n  $('applySpecialPrice').addEventListener('click',applySpecialPrice);\n  $('clearSpecialPrice').addEventListener('click',clearSpecialPrice);",
    1,
)
html = html.replace(
    "states.clear();resetSelection();$('unitSelect').innerHTML='';",
    "states.clear();prices.clear();resetSelection();$('unitSelect').innerHTML='';",
    1,
)

required = ['id="basePrice"','id="specialPrice"','price_override','saveBasePrice','applySpecialPrice','clearSpecialPrice']
missing = [item for item in required if item not in html]
if missing:
    raise SystemExit('Patch incomplet: '+', '.join(missing))

path.write_text(html, encoding='utf-8')
print('Tarification propriétaire LOC appliquée.')
