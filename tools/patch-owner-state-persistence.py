from pathlib import Path

path = Path('gestion.html')
html = path.read_text(encoding='utf-8')

marker = 'DIGIY OWNER STATE VERIFY V1'
if marker in html:
    print('Vérification des états propriétaire déjà posée.')
    raise SystemExit(0)

old = '''async function applyState(status){
  const dates=selectedDates();
  if(!dates.length)return msg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
  if(!unitId)return msg(saveStatus,'⚠️ Aucun hébergement sélectionné.',true);
  msg(saveStatus,'Enregistrement de l’état…');
  const {data,error}=await db.rpc('digiy_loc_set_unit_calendar_state_v2',{
    p_unit_id:unitId,
    p_days:dates,
    p_status:status
  });
  if(error)return msg(saveStatus,'⚠️ État refusé : '+error.message,true);
  const rows=Array.isArray(data)?data:[];
  if(rows.length!==dates.length)return msg(saveStatus,'⚠️ Réponse incomplète de la base.',true);
  rows.forEach(row=>{
    if(row.status==='available')states.delete(row.day);
    else states.set(row.day,row.status);
  });
  const label=status==='available'?'Disponible':status==='occupied'?'Occupé':'Fermé';
  msg(saveStatus,'✓ '+label+' enregistré sur '+dates.length+(dates.length===1?' date.':' dates.'));
  resetSelection();
  render();
}
'''

new = '''// DIGIY OWNER STATE VERIFY V1 — la base reste la seule mémoire de vérité.
async function applyState(status){
  const dates=selectedDates();
  if(!dates.length)return msg(saveStatus,'⚠️ Sélectionnez une date ou une période.',true);
  if(!unitId)return msg(saveStatus,'⚠️ Aucun hébergement sélectionné.',true);

  const buttons=[$('makeAvailable'),$('makeOccupied'),$('makeClosed')].filter(Boolean);
  buttons.forEach(button=>button.disabled=true);
  msg(saveStatus,'Enregistrement et vérification…');

  try{
    const {data,error}=await db.rpc('digiy_loc_set_unit_calendar_state_v2',{
      p_unit_id:unitId,
      p_days:dates,
      p_status:status
    });
    if(error)return msg(saveStatus,'⚠️ État refusé : '+error.message,true);

    const rows=Array.isArray(data)?data:[];
    const returnedDays=new Set(rows.map(row=>String(row.day)));
    if(rows.length!==dates.length || dates.some(day=>!returnedDays.has(day))){
      return msg(saveStatus,'⚠️ La base n’a pas confirmé toute la sélection.',true);
    }

    // Ne jamais valider sur la seule réponse du clic : on relit la base.
    await loadData();
    const persisted=status==='available'
      ? dates.every(day=>!states.has(day))
      : dates.every(day=>states.get(day)===status);

    if(!persisted){
      render();
      return msg(saveStatus,'⚠️ État non retrouvé après relecture. Aucun faux succès affiché.',true);
    }

    const label=status==='available'?'Disponible':status==='occupied'?'Occupé':'Fermé';
    resetSelection();
    render();
    msg(saveStatus,'✓ '+label+' confirmé en base sur '+dates.length+(dates.length===1?' date.':' dates.'));
  }finally{
    buttons.forEach(button=>button.disabled=false);
  }
}

let ownerResyncBusy=false;
async function resyncOwnerCalendar(){
  if(ownerResyncBusy||!unitId||managerPanel.classList.contains('hidden'))return;
  ownerResyncBusy=true;
  try{
    await loadData();
    render();
  }finally{
    ownerResyncBusy=false;
  }
}
window.addEventListener('focus',resyncOwnerCalendar);
document.addEventListener('visibilitychange',()=>{
  if(document.visibilityState==='visible')resyncOwnerCalendar();
});
'''

if old not in html:
    raise SystemExit('Bloc applyState attendu introuvable : arrêt sans modification.')

html = html.replace(old, new, 1)
path.write_text(html, encoding='utf-8')
print('Mémoire des états LOC propriétaire : relecture et vérification Supabase activées.')
