from pathlib import Path
import re

path=Path('gestion.html')
s=path.read_text(encoding='utf-8')
marker='DIGIY SARLAT PRIVATE RESERVATION VERIFY V2'
if marker in s:
    print('Vérification réservation Sarlat V2 déjà présente.')
    raise SystemExit(0)

pattern=re.compile(r"async function savePrivateReservation\(\)\{.*?\n\}\n// DIGIY OWNER STATE VERIFY V1",re.S)
replacement=r'''// DIGIY SARLAT PRIVATE RESERVATION VERIFY V2 — même chaîne de vérité que le bouton Occupé.
async function savePrivateReservation(){
  const dates=selectedDates();
  if(!dates.length)return msg(saveStatus,'⚠️ Sélectionnez d’abord une date ou une période.',true);
  const guestName=$('guestName').value.trim(),guestPhone=$('guestPhone').value.trim();
  if(!guestName)return msg(saveStatus,'⚠️ Indiquez le nom du client.',true);
  if(!guestPhone)return msg(saveStatus,'⚠️ Indiquez le téléphone du client.',true);
  const button=$('saveReservation');button.disabled=true;msg(saveStatus,'Enregistrement et vérification…');
  try{
    const {data,error}=await db.rpc('digiy_loc_master_save_reservation_v1',{
      p_unit_id:unitId,p_start_day:dates[0],p_end_day:dates[dates.length-1],p_guest_name:guestName,p_guest_phone:guestPhone,p_source:$('reservationSource').value,p_note:$('reservationNote').value.trim()||null
    });
    if(error)return msg(saveStatus,'⚠️ Réservation non enregistrée : '+error.message,true);
    if(!data||!data.length)return msg(saveStatus,'⚠️ Réservation non retrouvée après écriture.',true);

    // Vérification réelle du statut Occupé dans la table calendrier.
    const {data:verifyRows,error:verifyError}=await db.from('digiy_loc_master_unit_calendar')
      .select('day,status')
      .eq('unit_id',unitId)
      .in('day',dates);
    if(verifyError)return msg(saveStatus,'⚠️ Réservation créée mais relecture calendrier impossible : '+verifyError.message,true);
    const verifyMap=new Map((verifyRows||[]).map(row=>[String(row.day),row.status]));
    if(!dates.every(day=>verifyMap.get(day)==='occupied')){
      return msg(saveStatus,'⚠️ Réservation créée mais les dates ne sont pas confirmées Occupé. Aucun faux succès affiché.',true);
    }

    // Mettre à jour l’écran proprio immédiatement depuis la vérité confirmée.
    dates.forEach(day=>states.set(day,'occupied'));

    // Recharger uniquement les fiches privées, sans pouvoir effacer l’état confirmé.
    const reservationResult=await db.from('digiy_loc_master_reservations')
      .select('id,unit_id,guest_name,guest_phone,source,start_day,end_day,note,created_at')
      .eq('unit_id',unitId)
      .gte('end_day',iso(today()))
      .order('start_day');
    if(!reservationResult.error) reservations=reservationResult.data||[];

    resetSelection();render();renderReservations();
    $('guestName').value='';$('guestPhone').value='';$('reservationNote').value='';

    // Même notification que la route rouge Occupé : fiche publique déjà ouverte = relecture immédiate.
    const syncPayload={type:'calendar-changed',unitId,dates,status:'occupied',ts:Date.now()};
    try{const channel=new BroadcastChannel('digiy-loc-sarlat');channel.postMessage(syncPayload);channel.close();}catch(_){ }
    try{localStorage.setItem('digiy-loc-sarlat-sync',JSON.stringify(syncPayload));}catch(_){ }

    msg(saveStatus,'✓ Réservation privée enregistrée · Occupé confirmé en base et synchronisation publique déclenchée.');
  }finally{button.disabled=false;}
}
// DIGIY OWNER STATE VERIFY V1'''

s2,count=pattern.subn(replacement,s,count=1)
if count!=1:
    raise SystemExit('Fonction savePrivateReservation Sarlat introuvable')
path.write_text(s2,encoding='utf-8')
print('Réservation privée Sarlat alignée sur la chaîne Occupé vérifiée + synchro publique.')
