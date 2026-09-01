from pathlib import Path

path = Path('gestion.html')
html = path.read_text(encoding='utf-8')

marker = "DIGIY OWNER STATE VERIFY V2"
if marker in html:
    print('Vérification statut LOC V2 déjà appliquée.')
    raise SystemExit(0)

old = '''    // Ne jamais valider sur la seule réponse du clic : on relit la base.\n    await loadData();\n    const persisted=status==='available'\n      ? dates.every(day=>!states.has(day))\n      : dates.every(day=>states.get(day)===status);\n\n    if(!persisted){\n      render();\n      return msg(saveStatus,'⚠️ État non retrouvé après relecture. Aucun faux succès affiché.',true);\n    }\n'''

new = '''    // DIGIY OWNER STATE VERIFY V2 — confirmer le statut sans dépendre du chargement des tarifs.\n    const {data:verifyRows,error:verifyError}=await db.from('digiy_loc_master_unit_calendar')\n      .select('day,status')\n      .eq('unit_id',unitId)\n      .in('day',dates);\n    if(verifyError){\n      render();\n      return msg(saveStatus,'⚠️ Relecture du statut impossible : '+verifyError.message,true);\n    }\n\n    const verifyMap=new Map((verifyRows||[]).map(row=>[String(row.day),row.status]));\n    const persisted=status==='available'\n      ? dates.every(day=>!verifyMap.has(day))\n      : dates.every(day=>verifyMap.get(day)===status);\n\n    if(!persisted){\n      render();\n      return msg(saveStatus,'⚠️ État non retrouvé après relecture. Aucun faux succès affiché.',true);\n    }\n\n    // Le statut est confirmé : mettre à jour l’affichage immédiatement.\n    if(status==='available') dates.forEach(day=>states.delete(day));\n    else dates.forEach(day=>states.set(day,status));\n'''

if old not in html:
    raise SystemExit('Bloc de vérification statut actuel introuvable')

html = html.replace(old, new, 1)
path.write_text(html, encoding='utf-8')
print('Vérification statut LOC séparée des tarifs et appliquée.')
