from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')
marker = 'DIGIY PUBLIC RESERVATION SYNC V6'
if marker in s:
    print('V6 déjà présent.')
    raise SystemExit(0)

old = '''                try {
                    const params = new URLSearchParams({
                        select: "day,status",
                        unit_id: "eq." + CFG.masterUnitId,
                        day: "gte." + todayIso,
                        order: "day.asc"
                    });
                    params.append("day", "lte." + CFG.lastDate);

                    const response = await fetch(
                        SUPABASE_URL + "/rest/v1/digiy_loc_master_unit_calendar?" + params.toString(),
                        { method: "GET", headers, cache: "no-store" }
                    );'''
new = '''                try {
                    // DIGIY PUBLIC RESERVATION SYNC V6 — filtre unique de période, sans doublon de paramètre day.
                    const params = new URLSearchParams({
                        select: "day,status",
                        unit_id: "eq." + CFG.masterUnitId,
                        and: `(day.gte.${todayIso},day.lte.${CFG.lastDate})`,
                        order: "day.asc"
                    });

                    const response = await fetch(
                        SUPABASE_URL + "/rest/v1/digiy_loc_master_unit_calendar?" + params.toString(),
                        { method: "GET", headers, cache: "no-store" }
                    );'''
if old not in s:
    raise SystemExit('Ancre requête calendrier introuvable')
s = s.replace(old, new, 1)

old = '''            window.DIGIY_SYNC_PUBLIC_LOC=refreshPublicLoc;
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
            });'''
new = '''            window.DIGIY_SYNC_PUBLIC_LOC=refreshPublicLoc;
            refreshPublicLoc();

            // DIGIY PUBLIC RESERVATION SYNC V6 — appliquer d'abord le signal proprio, puis confirmer par Supabase.
            function applyPublicSyncPayload(payload){
                if(!payload || payload.type!=='calendar-changed') return false;
                if(payload.unitId && payload.unitId!==CFG.masterUnitId) return false;
                const dates=Array.isArray(payload.dates)?payload.dates.filter(Boolean):[];
                if(!dates.length) return false;
                const blocked=new Set(CFG.blockedDates||[]);
                const closed=new Set(CFG.closedDates||[]);
                dates.forEach(day=>{
                    if(payload.status==='occupied'){
                        blocked.add(day);closed.delete(day);
                    }else if(payload.status==='closed'){
                        closed.add(day);blocked.delete(day);
                    }else if(payload.status==='available'){
                        blocked.delete(day);closed.delete(day);
                    }
                });
                CFG.blockedDates=Array.from(blocked).sort();
                CFG.closedDates=Array.from(closed).sort();
                if(window.DIGIY_REFRESH_PUBLIC_CALENDAR) window.DIGIY_REFRESH_PUBLIC_CALENDAR();
                return true;
            }

            // Même appareil : notification immédiate depuis gestion.html.
            try{
                const publicSyncChannel=new BroadcastChannel('digiy-loc-sarlat');
                publicSyncChannel.addEventListener('message',event=>{
                    if(applyPublicSyncPayload(event.data)) refreshPublicLoc();
                });
                window.DIGIY_PUBLIC_SYNC_CHANNEL=publicSyncChannel;
            }catch(_){ }

            window.addEventListener('storage',event=>{
                if(event.key!=='digiy-loc-sarlat-sync') return;
                let payload=null;
                try{payload=event.newValue?JSON.parse(event.newValue):null;}catch(_){ }
                applyPublicSyncPayload(payload);
                refreshPublicLoc();
            });'''
if old not in s:
    raise SystemExit('Ancre synchro publique introuvable')
s = s.replace(old, new, 1)

path.write_text(s, encoding='utf-8')
print('Synchro publique réservation Sarlat V6 appliquée.')
