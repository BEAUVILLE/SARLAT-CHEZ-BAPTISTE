from pathlib import Path
import re

path = Path('gestion.html')
html = path.read_text(encoding='utf-8')

marker = 'DIGIY OWNER STATE LOAD V3'
if marker in html:
    print('Relecture indépendante des états propriétaire déjà posée.')
    raise SystemExit(0)

pattern = re.compile(r"async function loadData\(\)\{.*?\}\nfunction updateSelection", re.S)
replacement = '''// DIGIY OWNER STATE LOAD V3 — les états se relisent indépendamment des tarifs.
async function loadData(){
  if(!unitId)return;
  const from=iso(new Date(today().getFullYear(),today().getMonth(),1,12));

  const stateResult=await db.from('digiy_loc_master_unit_calendar')
    .select('day,status')
    .eq('unit_id',unitId)
    .gte('day',from)
    .order('day');

  if(stateResult.error){
    msg(saveStatus,'⚠️ Lecture calendrier impossible : '+stateResult.error.message,true);
    return;
  }

  states=new Map((stateResult.data||[]).map(r=>[r.day,r.status]));

  // Les tarifs ne doivent jamais empêcher la restitution de Libre / Occupé / Fermé.
  const priceResult=await db.from('digiy_loc_master_unit_prices')
    .select('day,price_override')
    .eq('unit_id',unitId)
    .gte('day',from)
    .order('day');

  if(!priceResult.error){
    prices=new Map((priceResult.data||[]).map(r=>[r.day,Number(r.price_override)]));
  }
}
function updateSelection'''

html2, count = pattern.subn(replacement, html, count=1)
if count != 1:
    raise SystemExit('Bloc loadData attendu introuvable : arrêt sans modification.')

path.write_text(html2, encoding='utf-8')
print('Relecture propriétaire : états calendrier indépendants des tarifs.')
