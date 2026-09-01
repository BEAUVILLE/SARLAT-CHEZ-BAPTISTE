from pathlib import Path

path = Path('gestion.html')
html = path.read_text(encoding='utf-8')

marker = "DIGIY OWNER PUBLIC SYNC V3"
if marker in html:
    print('Notification publique LOC V3 déjà appliquée.')
    raise SystemExit(0)

anchor = "    const label=status==='available'?'Disponible':status==='occupied'?'Occupé':'Fermé';\n    resetSelection();\n    render();\n    msg(saveStatus,'✓ '+label+' confirmé en base sur '+dates.length+(dates.length===1?' date.':' dates.'));"

replacement = """    const label=status==='available'?'Disponible':status==='occupied'?'Occupé':'Fermé';
    resetSelection();
    render();
    msg(saveStatus,'✓ '+label+' confirmé en base sur '+dates.length+(dates.length===1?' date.':' dates.'));

    // DIGIY OWNER PUBLIC SYNC V3 — prévenir immédiatement une fiche publique déjà ouverte.
    const syncPayload={type:'calendar-changed',unitId,dates,status,ts:Date.now()};
    try{
      const channel=new BroadcastChannel('digiy-loc-sarlat');
      channel.postMessage(syncPayload);
      channel.close();
    }catch(_){ }
    try{localStorage.setItem('digiy-loc-sarlat-sync',JSON.stringify(syncPayload));}catch(_){ }"""

if anchor not in html:
    raise SystemExit('Point de notification statut introuvable')

html = html.replace(anchor, replacement, 1)
path.write_text(html, encoding='utf-8')
print('Notification immédiate vers la fiche publique activée.')
