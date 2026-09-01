from pathlib import Path

path = Path('gestion.html')
html = path.read_text(encoding='utf-8')

if "digiy_loc_master_unit_prices" in html:
    print('Tarifs LOC déjà séparés et vérifiés.')
    raise SystemExit(0)

old_load = '''  async function loadStates(){
    if(!unitId)return;
    const from=iso(new Date(today().getFullYear(),today().getMonth(),1,12));
    const {data,error}=await db.from('digiy_loc_master_unit_calendar').select('day,status,price_override').eq('unit_id',unitId).gte('day',from).order('day');
    if(error){setMsg(saveStatus,'⚠️ Lecture calendrier impossible : '+error.message,true);return;}
    states=new Map((data||[]).map(r=>[r.day,r.status]));
    prices=new Map((data||[]).filter(r=>r.price_override!=null).map(r=>[r.day,Number(r.price_override)]));
  }'''
new_load = '''  async function loadStates(){
    if(!unitId)return;
    const from=iso(new Date(today().getFullYear(),today().getMonth(),1,12));
    const [stateResult,priceResult]=await Promise.all([
      db.from('digiy_loc_master_unit_calendar').select('day,status').eq('unit_id',unitId).gte('day',from).order('day'),
      db.from('digiy_loc_master_unit_prices').select('day,price_override').eq('unit_id',unitId).gte('day',from).order('day')
    ]);
    if(stateResult.error){setMsg(saveStatus,'⚠️ Lecture calendrier impossible : '+stateResult.error.message,true);return;}
    if(priceResult.error){setMsg(saveStatus,'⚠️ Lecture tarifs impossible : '+priceResult.error.message,true);return;}
    states=new Map((stateResult.data||[]).map(r=>[r.day,r.status]));
    prices=new Map((priceResult.data||[]).map(r=>[r.day,Number(r.price_override)]));
  }'''
if old_load not in html:
    raise SystemExit('loadStates actuel introuvable')
html = html.replace(old_load,new_load,1)

start = html.find('  async function applyState(status){')
end = html.find("  $('sendCode').addEventListener", start)
if start < 0 or end < 0:
    raise SystemExit('Bloc fonctions calendrier introuvable')

new_functions = '''  async function applyState(status){
    const dates=selectedDates(); if(!dates.length)return setMsg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
    if(!unitId)return setMsg(saveStatus,'⚠️ Aucun hébergement sélectionné.',true);
    setMsg(saveStatus,'Enregistrement…');
    let error=null;
    if(status==='available'){
      ({error}=await db.from('digiy_loc_master_unit_calendar').delete().eq('unit_id',unitId).in('day',dates));
    }else{
      const rows=dates.map(day=>({unit_id:unitId,day,status,updated_at:new Date().toISOString()}));
      ({error}=await db.from('digiy_loc_master_unit_calendar').upsert(rows,{onConflict:'unit_id,day'}));
    }
    if(error)return setMsg(saveStatus,'⚠️ Enregistrement refusé : '+error.message,true);
    await loadStates(); resetSelection(); render();
    setMsg(saveStatus,'✓ Calendrier enregistré.');
  }

  async function saveBasePrice(){
    const value=Number($('basePrice').value);
    if(!Number.isFinite(value)||value<0)return setMsg(saveStatus,'⚠️ Indiquez un tarif de base valide.',true);
    if(!unitId)return setMsg(saveStatus,'⚠️ Aucun hébergement sélectionné.',true);
    setMsg(saveStatus,'Enregistrement du tarif de base…');
    const {data,error}=await db.from('digiy_loc_master_units')
      .update({base_price:value,price_currency:currency||'EUR',updated_at:new Date().toISOString()})
      .eq('id',unitId)
      .select('id,base_price,price_currency')
      .maybeSingle();
    if(error)return setMsg(saveStatus,'⚠️ Tarif de base refusé : '+error.message,true);
    if(!data)return setMsg(saveStatus,'⚠️ Le tarif de base n’a pas été confirmé par la base.',true);
    const unit=currentUnit(); if(unit){unit.base_price=Number(data.base_price);unit.price_currency=data.price_currency||currency||'EUR';}
    basePrice=Number(data.base_price); currency=data.price_currency||currency||'EUR'; syncBasePrice(); render();
    setMsg(saveStatus,'✓ Tarif de base enregistré en base : '+money(basePrice)+'.');
  }

  async function applySpecialPrice(){
    const dates=selectedDates(); if(!dates.length)return setMsg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
    const value=Number(String($('specialPrice').value).replace(',','.'));
    if(!Number.isFinite(value)||value<0)return setMsg(saveStatus,'⚠️ Indiquez un prix spécial valide.',true);
    setMsg(saveStatus,'Enregistrement du prix…');
    const rows=dates.map(day=>({unit_id:unitId,day,price_override:value,updated_at:new Date().toISOString()}));
    const {data,error}=await db.from('digiy_loc_master_unit_prices')
      .upsert(rows,{onConflict:'unit_id,day'})
      .select('day,price_override');
    if(error)return setMsg(saveStatus,'⚠️ Prix refusé : '+error.message,true);
    if(!data||data.length!==dates.length)return setMsg(saveStatus,'⚠️ Le prix n’a pas été confirmé pour toute la sélection.',true);
    data.forEach(row=>prices.set(row.day,Number(row.price_override)));
    render();
    const zone=dates.length===1?fmt(parse(dates[0])):fmt(parse(dates[0]))+' → '+fmt(parse(dates[dates.length-1]));
    setMsg(saveStatus,'✓ Prix enregistré en base : '+money(value)+' · '+zone+'.');
  }

  async function clearSpecialPrice(){
    const dates=selectedDates(); if(!dates.length)return setMsg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
    setMsg(saveStatus,'Retour au tarif de base…');
    const {error}=await db.from('digiy_loc_master_unit_prices').delete().eq('unit_id',unitId).in('day',dates);
    if(error)return setMsg(saveStatus,'⚠️ Retour au tarif de base refusé : '+error.message,true);
    dates.forEach(day=>prices.delete(day));
    render();
    setMsg(saveStatus,'✓ Tarif de base rétabli sur la sélection.');
  }

'''
html = html[:start] + new_functions + html[end:]

required = ["digiy_loc_master_unit_prices","select('day,status')","Prix enregistré en base","status==='available'"]
missing = [x for x in required if x not in html]
if missing:
    raise SystemExit('Réparation incomplète: '+', '.join(missing))

path.write_text(html,encoding='utf-8')
print('Tarifs LOC séparés des disponibilités et vérification d’écriture activée.')
