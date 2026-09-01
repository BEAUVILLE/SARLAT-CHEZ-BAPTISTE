from pathlib import Path

path=Path('gestion.html')
s=path.read_text(encoding='utf-8')
marker='DIGIY SARLAT PRIVATE RESERVATIONS V1'
if marker in s:
    print('Réservations privées Sarlat déjà présentes.')
    raise SystemExit(0)

# CSS
old='button,input,select{font:inherit}'
new='button,input,select,textarea{font:inherit}'
if old not in s: raise SystemExit('CSS font anchor introuvable')
s=s.replace(old,new,1)

old='@media(max-width:560px){.price-grid{grid-template-columns:1fr}'
new='''.reservation-box{margin-top:16px;padding:15px;border:1px solid #d8c8b6;border-radius:18px;background:#fff}.reservation-box h3{margin:0 0 5px;font-size:18px}.reservation-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.reservation-grid .wide{grid-column:1/-1}.reservation-box textarea{width:100%;min-height:82px;resize:vertical;border:1px solid #cdbba8;border-radius:14px;padding:12px;font:inherit}.reservation-list{display:grid;gap:9px;margin-top:12px}.reservation-card{padding:12px;border:1px solid #e1d2c2;border-radius:15px;background:#fffaf1}.reservation-card strong{display:block;font-size:15px}.reservation-meta{margin-top:4px;color:#6e5845;font-size:12px;font-weight:750;line-height:1.45}.reservation-note{margin-top:6px;font-size:12px;line-height:1.45;color:#4d3b2e}.reservation-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}.reservation-actions a{display:inline-flex;align-items:center;justify-content:center;min-height:38px;padding:7px 11px;border-radius:999px;text-decoration:none;font-size:12px;font-weight:950}.sms-action{background:#e7f1ff;color:#174b86}.wa-action{background:#def7e9;color:#17633e}.guest-mark{font-size:9px;line-height:1}.empty-reservations{color:#6e5845;font-size:12px;font-weight:750;padding:9px 0}/* DIGIY SARLAT PRIVATE RESERVATIONS V1 */@media(max-width:560px){.reservation-grid{grid-template-columns:1fr}.reservation-grid .wide{grid-column:auto}.price-grid{grid-template-columns:1fr}'''
if old not in s: raise SystemExit('CSS media anchor introuvable')
s=s.replace(old,new,1)

# HTML blocks
old='''<div class="pricing"><div class="pricing-title">🏷️ Prix de la sélection</div><p class="pricing-note">1 date = prix du jour · plusieurs dates = prix de la période.</p><div class="price-grid"><div class="field"><label for="specialPrice">Prix spécial / nuitée</label><input id="specialPrice" type="number" min="0" step="0.01" inputmode="decimal" placeholder="Ex. 95"></div><button class="btn primary" id="applySpecialPrice" type="button">Appliquer ce prix</button></div><div class="price-actions"><button class="btn ghost" id="clearSpecialPrice" type="button">↩ Revenir au tarif de base</button></div></div>
<p class="status" id="saveStatus" aria-live="polite"></p>'''
new='''<div class="pricing"><div class="pricing-title">🏷️ Prix de la sélection</div><p class="pricing-note">1 date = prix du jour · plusieurs dates = prix de la période.</p><div class="price-grid"><div class="field"><label for="specialPrice">Prix spécial / nuitée</label><input id="specialPrice" type="number" min="0" step="0.01" inputmode="decimal" placeholder="Ex. 95"></div><button class="btn primary" id="applySpecialPrice" type="button">Appliquer ce prix</button></div><div class="price-actions"><button class="btn ghost" id="clearSpecialPrice" type="button">↩ Revenir au tarif de base</button></div></div>
<div class="reservation-box">
<h3>👤 Réservation privée</h3>
<p class="pricing-note">Sélectionnez la ou les dates dans le calendrier, puis rattachez le client. Ces informations restent uniquement dans votre accès propriétaire.</p>
<div class="reservation-grid">
<div class="field"><label for="guestName">Nom du client</label><input id="guestName" type="text" autocomplete="name" placeholder="Nom et prénom"></div>
<div class="field"><label for="guestPhone">Téléphone</label><input id="guestPhone" type="tel" autocomplete="tel" placeholder="+33… / +221…"></div>
<div class="field"><label for="reservationSource">Provenance</label><select id="reservationSource"><option value="Booking.com">Booking.com</option><option value="Airbnb">Airbnb</option><option value="WhatsApp">WhatsApp</option><option value="Direct">Direct</option><option value="Autre">Autre</option></select></div>
<div class="field"><label>Dates</label><input id="reservationDates" type="text" readonly placeholder="Sélectionnez dans le calendrier"></div>
<div class="field wide"><label for="reservationNote">Note privée · facultatif</label><textarea id="reservationNote" placeholder="Heure d’arrivée, demande particulière, référence…"></textarea></div>
</div>
<button class="btn dark" id="saveReservation" type="button" style="margin-top:10px">🔒 Enregistrer la réservation</button>
</div>
<div class="reservation-box">
<h3>📒 Réservations à venir</h3>
<p class="pricing-note">Nom et téléphone ne quittent jamais l’espace propriétaire.</p>
<div class="reservation-list" id="reservationList"></div>
</div>
<p class="status" id="saveStatus" aria-live="polite"></p>'''
if old not in s: raise SystemExit('HTML pricing anchor introuvable')
s=s.replace(old,new,1)

# JS state
old="let units=[],unitId=null,current=new Date(),states=new Map(),prices=new Map(),basePrice=78,currency='EUR',start=null,end=null;"
new="let units=[],unitId=null,current=new Date(),states=new Map(),prices=new Map(),reservations=[],basePrice=78,currency='EUR',start=null,end=null;"
if old not in s: raise SystemExit('JS state anchor introuvable')
s=s.replace(old,new,1)

# loadData append private reservation load after price load
old='''  if(!priceResult.error){
    prices=new Map((priceResult.data||[]).map(r=>[r.day,Number(r.price_override)]));
  }
}'''
new='''  if(!priceResult.error){
    prices=new Map((priceResult.data||[]).map(r=>[r.day,Number(r.price_override)]));
  }

  const reservationResult=await db.from('digiy_loc_master_reservations')
    .select('id,unit_id,guest_name,guest_phone,source,start_day,end_day,note,created_at')
    .eq('unit_id',unitId)
    .gte('end_day',iso(today()))
    .order('start_day');
  if(reservationResult.error){
    reservations=[];
    console.warn('[SARLAT OWNER] Réservations privées indisponibles',reservationResult.error);
  }else{
    reservations=reservationResult.data||[];
  }
  renderReservations();
}'''
if old not in s: raise SystemExit('loadData anchor introuvable')
s=s.replace(old,new,1)

# selection field sync
old="function updateSelection(){if(!start)return $('selectionLabel').textContent='Sélection : aucune date';$('selectionLabel').textContent=end&&iso(end)!==iso(start)?'Sélection : '+fmt(start)+' → '+fmt(end):'Sélection : '+fmt(start)}"
new="function updateSelection(){const datesInput=$('reservationDates');if(!start){$('selectionLabel').textContent='Sélection : aucune date';if(datesInput)datesInput.value='';return}const label=end&&iso(end)!==iso(start)?fmt(start)+' → '+fmt(end):fmt(start);$('selectionLabel').textContent='Sélection : '+label;if(datesInput)datesInput.value=label}"
if old not in s: raise SystemExit('updateSelection anchor introuvable')
s=s.replace(old,new,1)

# render calendar guest marker
old="b.innerHTML='<span>'+d+'</span><small class=\"day-price\">'+money(shown)+'</small>';if(date<today())b.disabled=true;"
new="const booking=reservations.find(r=>key>=r.start_day&&key<=r.end_day);b.innerHTML='<span>'+d+'</span><small class=\"day-price\">'+money(shown)+'</small>'+(booking?'<small class=\"guest-mark\">👤</small>':'');if(booking)b.title=booking.guest_name+' · '+booking.guest_phone;if(date<today())b.disabled=true;"
if old not in s: raise SystemExit('render day anchor introuvable')
s=s.replace(old,new,1)

# Add reservation functions before applyState marker
anchor='// DIGIY OWNER STATE VERIFY V1 — la base reste la seule mémoire de vérité.\nasync function applyState(status){'
insert='''function reservationMessage(r){
  const dates=r.start_day===r.end_day?r.start_day:(r.start_day+' au '+r.end_day);
  return 'Bonjour '+r.guest_name+', concernant votre séjour Chez Baptiste Sarlat du '+dates+', je vous contacte pour vous transmettre des informations complémentaires.';
}
function renderReservations(){
  const box=$('reservationList');if(!box)return;
  box.innerHTML='';
  if(!reservations.length){const empty=document.createElement('div');empty.className='empty-reservations';empty.textContent='Aucune fiche client enregistrée à venir.';box.appendChild(empty);return;}
  reservations.forEach(r=>{
    const card=document.createElement('article');card.className='reservation-card';
    const name=document.createElement('strong');name.textContent='👤 '+r.guest_name;card.appendChild(name);
    const meta=document.createElement('div');meta.className='reservation-meta';meta.textContent=(r.start_day===r.end_day?r.start_day:r.start_day+' → '+r.end_day)+' · '+r.guest_phone+(r.source?' · '+r.source:'');card.appendChild(meta);
    if(r.note){const note=document.createElement('div');note.className='reservation-note';note.textContent=r.note;card.appendChild(note);}
    const actions=document.createElement('div');actions.className='reservation-actions';
    const sms=document.createElement('a');sms.className='sms-action';sms.textContent='📩 SMS';sms.href='sms:'+r.guest_phone+'?body='+encodeURIComponent(reservationMessage(r));actions.appendChild(sms);
    const digits=String(r.guest_phone||'').replace(/\\D/g,'');
    if(digits){const wa=document.createElement('a');wa.className='wa-action';wa.textContent='💬 WhatsApp';wa.href='https://wa.me/'+digits+'?text='+encodeURIComponent(reservationMessage(r));wa.target='_blank';wa.rel='noopener';actions.appendChild(wa);}
    card.appendChild(actions);box.appendChild(card);
  });
}
async function savePrivateReservation(){
  const dates=selectedDates();
  if(!dates.length)return msg(saveStatus,'⚠️ Sélectionnez d’abord une date ou une période.',true);
  const guestName=$('guestName').value.trim(),guestPhone=$('guestPhone').value.trim();
  if(!guestName)return msg(saveStatus,'⚠️ Indiquez le nom du client.',true);
  if(!guestPhone)return msg(saveStatus,'⚠️ Indiquez le téléphone du client.',true);
  const button=$('saveReservation');button.disabled=true;msg(saveStatus,'Enregistrement de la réservation…');
  try{
    const {data,error}=await db.rpc('digiy_loc_master_save_reservation_v1',{
      p_unit_id:unitId,p_start_day:dates[0],p_end_day:dates[dates.length-1],p_guest_name:guestName,p_guest_phone:guestPhone,p_source:$('reservationSource').value,p_note:$('reservationNote').value.trim()||null
    });
    if(error)return msg(saveStatus,'⚠️ Réservation non enregistrée : '+error.message,true);
    if(!data||!data.length)return msg(saveStatus,'⚠️ Réservation non retrouvée après écriture.',true);
    await loadData();
    resetSelection();render();renderReservations();
    $('guestName').value='';$('guestPhone').value='';$('reservationNote').value='';
    msg(saveStatus,'✓ Réservation privée enregistrée et dates confirmées Occupé.');
  }finally{button.disabled=false;}
}
// DIGIY OWNER STATE VERIFY V1 — la base reste la seule mémoire de vérité.
async function applyState(status){'''
if anchor not in s: raise SystemExit('applyState anchor introuvable')
s=s.replace(anchor,insert,1)

# events
old="$('unitSelect').addEventListener('change',async e=>{unitId=e.target.value;states.clear();prices.clear();resetSelection();syncBase();await loadData();render()});"
new="$('unitSelect').addEventListener('change',async e=>{unitId=e.target.value;states.clear();prices.clear();reservations=[];resetSelection();syncBase();await loadData();render();renderReservations()});"
if old not in s: raise SystemExit('unitSelect event anchor introuvable')
s=s.replace(old,new,1)

old="$('clearSpecialPrice').addEventListener('click',clearSpecialPrice);$('logout').addEventListener('click',async()=>{await db.auth.signOut();units=[];unitId=null;states.clear();prices.clear();resetSelection();showLogin()});"
new="$('clearSpecialPrice').addEventListener('click',clearSpecialPrice);$('saveReservation').addEventListener('click',savePrivateReservation);$('logout').addEventListener('click',async()=>{await db.auth.signOut();units=[];unitId=null;states.clear();prices.clear();reservations=[];resetSelection();showLogin()});"
if old not in s: raise SystemExit('events logout anchor introuvable')
s=s.replace(old,new,1)

path.write_text(s,encoding='utf-8')
print('Réservations privées propriétaire ajoutées à Sarlat sans modifier index.html.')
