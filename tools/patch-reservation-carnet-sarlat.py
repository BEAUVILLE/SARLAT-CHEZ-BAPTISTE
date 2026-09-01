from pathlib import Path

path=Path('gestion.html')
s=path.read_text(encoding='utf-8')
marker='DIGIY SARLAT RESERVATION CARNET V2'
if marker in s:
    print('Carnet Sarlat déjà présent.')
    raise SystemExit(0)

# CSS carnet visible et lisible
css_anchor='.empty-reservations{color:#6e5845;font-size:12px;font-weight:750;padding:9px 0}/* DIGIY SARLAT PRIVATE RESERVATIONS V1 */'
css_new='''.empty-reservations{color:#6e5845;font-size:12px;font-weight:750;padding:9px 0}.reservation-carnet{border:2px solid #315b4355;background:linear-gradient(145deg,#ffffff,#f7f2ea)}.reservation-carnet-head{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;flex-wrap:wrap}.reservation-carnet-head h3{margin:0}.reservation-count{margin-top:8px;font-size:12px;font-weight:1000;color:#315b43}.reservation-card{box-shadow:0 7px 18px rgba(61,43,22,.06)}.reservation-card.history{opacity:.78}.reservation-card-head{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap}.reservation-badge{display:inline-flex;padding:4px 8px;border-radius:999px;background:#e3f1e7;color:#245035;font-size:10px;font-weight:1000}.reservation-card.history .reservation-badge{background:#eee7df;color:#6e5845}.reservation-note{padding:8px 10px;border-radius:11px;background:#fff;border-left:4px solid #c99743;font-weight:800}.carnet-refresh{min-height:36px;padding:7px 11px;font-size:11px}/* DIGIY SARLAT RESERVATION CARNET V2 */ /* DIGIY SARLAT PRIVATE RESERVATIONS V1 */'''
if css_anchor not in s: raise SystemExit('CSS carnet anchor introuvable')
s=s.replace(css_anchor,css_new,1)

# Retirer l'ancien listing placé trop bas
old_listing='''<div class="reservation-box">\n<h3>📒 Réservations à venir</h3>\n<p class="pricing-note">Nom et téléphone ne quittent jamais l’espace propriétaire.</p>\n<div class="reservation-list" id="reservationList"></div>\n</div>\n'''
if old_listing not in s: raise SystemExit('Ancien listing introuvable')
s=s.replace(old_listing,'',1)

# Poser le carnet juste sous les actions calendrier
state_anchor='<div class="state-actions"><button class="freeBtn" id="makeAvailable" type="button">🟢 Disponible</button><button class="occBtn" id="makeOccupied" type="button">🔴 Occupé</button><button class="closeBtn" id="makeClosed" type="button">⚫ Fermé</button></div>\n'
carnet='''<div class="state-actions"><button class="freeBtn" id="makeAvailable" type="button">🟢 Disponible</button><button class="occBtn" id="makeOccupied" type="button">🔴 Occupé</button><button class="closeBtn" id="makeClosed" type="button">⚫ Fermé</button></div>\n<div class="reservation-box reservation-carnet" id="reservationCarnet">\n<div class="reservation-carnet-head"><div><h3>📒 Carnet des réservations</h3><p class="pricing-note">Vos fiches client et vos notes privées, à venir comme passées.</p></div><button class="btn ghost carnet-refresh" id="refreshReservations" type="button">↻ Rafraîchir</button></div>\n<div class="reservation-count" id="reservationCount">Chargement du carnet…</div>\n<div class="reservation-list" id="reservationList"></div>\n</div>\n'''
if state_anchor not in s: raise SystemExit('State actions anchor introuvable')
s=s.replace(state_anchor,carnet,1)

# Remplacer la lecture directe limitée aux prochaines réservations par le RPC propriétaire complet
old_load='''  const reservationResult=await db.from('digiy_loc_master_reservations')\n    .select('id,unit_id,guest_name,guest_phone,source,start_day,end_day,note,created_at')\n    .eq('unit_id',unitId)\n    .gte('end_day',iso(today()))\n    .order('start_day');\n  if(reservationResult.error){\n    reservations=[];\n    console.warn('[SARLAT OWNER] Réservations privées indisponibles',reservationResult.error);\n  }else{\n    reservations=reservationResult.data||[];\n  }\n  renderReservations();\n'''
if old_load not in s: raise SystemExit('Lecture réservations loadData introuvable')
s=s.replace(old_load,'  await loadReservationCarnet();\n',1)

# Ajouter le chargeur propriétaire dédié avant updateSelection
insert_anchor='function updateSelection(){'
loader='''async function loadReservationCarnet(){\n  const count=$('reservationCount');\n  if(count) count.textContent='Chargement du carnet…';\n  if(!unitId){reservations=[];renderReservations();return false;}\n  const {data,error}=await db.rpc('digiy_loc_master_list_reservations_v1',{p_unit_id:unitId});\n  if(error){\n    reservations=[];\n    if(count) count.textContent='⚠️ Carnet indisponible';\n    console.warn('[SARLAT OWNER] Carnet réservations indisponible',error);\n    renderReservations();\n    return false;\n  }\n  reservations=Array.isArray(data)?data:[];\n  renderReservations();\n  return true;\n}\n'''
if insert_anchor not in s: raise SystemExit('updateSelection anchor introuvable')
s=s.replace(insert_anchor,loader+insert_anchor,1)

# Nouveau rendu carnet : toutes les fiches, notes visibles, badge à venir/historique
start=s.find('function renderReservations(){')
end=s.find('// DIGIY SARLAT PRIVATE RESERVATION VERIFY V2',start)
if start<0 or end<0: raise SystemExit('renderReservations boundaries introuvables')
new_render='''function renderReservations(){\n  const box=$('reservationList'),count=$('reservationCount');if(!box)return;\n  box.innerHTML='';\n  if(count) count.textContent=reservations.length+' fiche'+(reservations.length===1?'':'s')+' enregistrée'+(reservations.length===1?'':'s');\n  if(!reservations.length){const empty=document.createElement('div');empty.className='empty-reservations';empty.textContent='Aucune fiche client enregistrée.';box.appendChild(empty);return;}\n  const todayKey=iso(today());\n  reservations.forEach(r=>{\n    const upcoming=String(r.end_day)>=todayKey;\n    const card=document.createElement('article');card.className='reservation-card'+(upcoming?'':' history');\n    const head=document.createElement('div');head.className='reservation-card-head';\n    const name=document.createElement('strong');name.textContent='👤 '+r.guest_name;head.appendChild(name);\n    const badge=document.createElement('span');badge.className='reservation-badge';badge.textContent=upcoming?'À venir':'Historique';head.appendChild(badge);\n    card.appendChild(head);\n    const startDate=fmt(parse(r.start_day)),endDate=fmt(parse(r.end_day));\n    const meta=document.createElement('div');meta.className='reservation-meta';meta.textContent=(r.start_day===r.end_day?startDate:startDate+' → '+endDate)+' · '+r.guest_phone+(r.source?' · '+r.source:'');card.appendChild(meta);\n    const note=document.createElement('div');note.className='reservation-note';note.textContent=r.note?'📝 '+r.note:'📝 Aucune note privée';card.appendChild(note);\n    const actions=document.createElement('div');actions.className='reservation-actions';\n    const sms=document.createElement('a');sms.className='sms-action';sms.textContent='📩 SMS';sms.href='sms:'+r.guest_phone+'?body='+encodeURIComponent(reservationMessage(r));actions.appendChild(sms);\n    const digits=String(r.guest_phone||'').replace(/\\D/g,'');\n    if(digits){const wa=document.createElement('a');wa.className='wa-action';wa.textContent='💬 WhatsApp';wa.href='https://wa.me/'+digits+'?text='+encodeURIComponent(reservationMessage(r));wa.target='_blank';wa.rel='noopener';actions.appendChild(wa);}\n    card.appendChild(actions);box.appendChild(card);\n  });\n}\n'''
s=s[:start]+new_render+s[end:]

# Après sauvegarde, recharger le carnet complet via le RPC dédié
old_save_reload='''    // Recharger uniquement les fiches privées, sans pouvoir effacer l’état confirmé.\n    const reservationResult=await db.from('digiy_loc_master_reservations')\n      .select('id,unit_id,guest_name,guest_phone,source,start_day,end_day,note,created_at')\n      .eq('unit_id',unitId)\n      .gte('end_day',iso(today()))\n      .order('start_day');\n    if(!reservationResult.error) reservations=reservationResult.data||[];\n\n'''
if old_save_reload not in s: raise SystemExit('Reload réservation après save introuvable')
s=s.replace(old_save_reload,'    // Recharger le carnet propriétaire complet, notes incluses.\n    await loadReservationCarnet();\n\n',1)

# Bouton manuel de rafraîchissement
listener_anchor="$ ('dummy')"  # placeholder never used
old_event="$('clearSpecialPrice').addEventListener('click',clearSpecialPrice);$('saveReservation').addEventListener('click',savePrivateReservation);"
new_event="$('clearSpecialPrice').addEventListener('click',clearSpecialPrice);$('saveReservation').addEventListener('click',savePrivateReservation);$('refreshReservations').addEventListener('click',loadReservationCarnet);"
if old_event not in s: raise SystemExit('Event réservation anchor introuvable')
s=s.replace(old_event,new_event,1)

path.write_text(s,encoding='utf-8')
print('Carnet propriétaire Sarlat ajouté : notes visibles dans l’interface, historique inclus.')
