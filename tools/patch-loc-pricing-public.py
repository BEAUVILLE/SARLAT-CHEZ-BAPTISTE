from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

marker = 'DIGIY PUBLIC LIVE SYNC V2'
if marker in s:
    print('Synchronisation publique live V2 déjà appliquée.')
    raise SystemExit(0)

start_anchor = '            (async function syncMasterCalendar() {'
if start_anchor not in s:
    raise SystemExit('Début syncMasterCalendar introuvable')
s = s.replace(start_anchor, '            async function syncMasterCalendar() {', 1)

sync_start = s.find('            // ===== SYNCHRONISATION PUBLIQUE DU MASTER LOC =====')
if sync_start < 0:
    raise SystemExit('Bloc synchronisation publique introuvable')

end_anchor = '            })();\n\n            // ===== FORMULAIRE ====='
end_pos = s.find(end_anchor, sync_start)
if end_pos < 0:
    raise SystemExit('Fin syncMasterCalendar introuvable')

live = '''            }

            // DIGIY PUBLIC LIVE SYNC V2 — Supabase est la mémoire commune Proprio/Public.
            let publicLocSyncBusy=false;
            async function refreshPublicLoc(){
                if(publicLocSyncBusy)return;
                publicLocSyncBusy=true;
                try{await syncMasterCalendar();}
                finally{publicLocSyncBusy=false;}
            }

            window.DIGIY_SYNC_PUBLIC_LOC=refreshPublicLoc;
            refreshPublicLoc();

            // Même appareil : notification immédiate depuis gestion.html.
            try{
                const publicSyncChannel=new BroadcastChannel('digiy-loc-sarlat');
                publicSyncChannel.addEventListener('message',event=>{
                    if(event.data&&event.data.type==='calendar-changed')refreshPublicLoc();
                });
                window.DIGIY_PUBLIC_SYNC_CHANNEL=publicSyncChannel;
            }catch(_){ }

            window.addEventListener('storage',event=>{
                if(event.key==='digiy-loc-sarlat-sync')refreshPublicLoc();
            });

            // Retour sur l’onglet : relecture immédiate de Supabase.
            window.addEventListener('focus',refreshPublicLoc);
            document.addEventListener('visibilitychange',()=>{
                if(document.visibilityState==='visible')refreshPublicLoc();
            });

            // Autre appareil / autre navigateur : resynchronisation régulière.
            setInterval(()=>{
                if(document.visibilityState==='visible')refreshPublicLoc();
            },15000);

            // ===== FORMULAIRE ====='''

s = s[:end_pos] + live + s[end_pos + len(end_anchor):]
path.write_text(s, encoding='utf-8')
print('Synchronisation Proprio → Supabase → Public activée en continu.')
