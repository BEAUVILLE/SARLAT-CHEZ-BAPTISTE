from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

marker = 'DIGIY PUBLIC STATE SYNC V4'
if marker in s:
    print('Synchronisation publique V4 déjà présente.')
    raise SystemExit(0)

pattern = re.compile(
    r"            // ===== SYNCHRONISATION PUBLIQUE DU MASTER LOC =====\n"
    r"            // DIGIY PUBLIC STATE SYNC V3.*?\n"
    r"            async function syncMasterCalendar\(\) \{.*?\n"
    r"            \}\n\n"
    r"            // DIGIY PUBLIC LIVE SYNC V2",
    re.S,
)

replacement = '''            // ===== SYNCHRONISATION PUBLIQUE DU MASTER LOC =====
            // DIGIY PUBLIC STATE SYNC V4 — états calendrier lus sans dépendre du SDK/CDN Supabase.
            async function syncMasterCalendar() {
                if (!CFG.masterUnitId) return;

                const SUPABASE_URL = "https://wesqmwjjtsefyjnluosj.supabase.co";
                const PUBLIC_KEY = "sb_publishable_tGHItRgeWDmGjnd0CK1DVQ_BIep4Ug3";
                const todayIso = localIso(new Date());

                // 1) PRIORITÉ ABSOLUE : disponibilité via REST natif du navigateur.
                try {
                    const params = new URLSearchParams({
                        select: "day,status",
                        unit_id: "eq." + CFG.masterUnitId,
                        day: "gte." + todayIso,
                        order: "day.asc"
                    });
                    // URLSearchParams ne peut porter deux fois `day` via objet : ajouter la borne haute séparément.
                    params.append("day", "lte." + CFG.lastDate);

                    const response = await fetch(
                        SUPABASE_URL + "/rest/v1/digiy_loc_master_unit_calendar?" + params.toString(),
                        {
                            method: "GET",
                            headers: {
                                apikey: PUBLIC_KEY,
                                Accept: "application/json"
                            },
                            cache: "no-store"
                        }
                    );

                    if (!response.ok) {
                        throw new Error("HTTP " + response.status + " " + (await response.text()));
                    }

                    const rows = await response.json();
                    const safeRows = Array.isArray(rows) ? rows : [];
                    CFG.blockedDates = safeRows.filter(row => row.status === "occupied").map(row => row.day);
                    CFG.closedDates = safeRows.filter(row => row.status === "closed").map(row => row.day);

                    if (window.DIGIY_RENDER_AVAILABILITY) {
                        window.DIGIY_RENDER_AVAILABILITY(safeRows);
                    }
                    if (window.DIGIY_REFRESH_PUBLIC_CALENDAR) {
                        window.DIGIY_REFRESH_PUBLIC_CALENDAR();
                    }
                } catch (error) {
                    console.warn("[SARLAT MASTER] Lecture calendrier REST indisponible, repli local conservé.", error);
                    return;
                }

                // 2) Tarifs : logique existante conservée, sans jamais bloquer les états.
                if (!window.supabase) return;

                const publicDb = window.supabase.createClient(
                    SUPABASE_URL,
                    PUBLIC_KEY,
                    {
                        auth: {
                            persistSession: false,
                            autoRefreshToken: false,
                            detectSessionInUrl: false
                        }
                    }
                );

                try {
                    const [unitResult, priceResult] = await Promise.all([
                        publicDb
                            .from("digiy_loc_master_units")
                            .select("base_price,price_currency")
                            .eq("id", CFG.masterUnitId)
                            .single(),
                        publicDb
                            .from("digiy_loc_master_unit_prices")
                            .select("day,price_override")
                            .eq("unit_id", CFG.masterUnitId)
                            .gte("day", todayIso)
                            .lte("day", CFG.lastDate)
                            .order("day")
                    ]);

                    if (!unitResult.error) {
                        const liveBase = Number(unitResult.data && unitResult.data.base_price);
                        if (Number.isFinite(liveBase) && liveBase >= 0) CFG.eur = liveBase;
                    }

                    if (!priceResult.error) {
                        const priceRows = Array.isArray(priceResult.data) ? priceResult.data : [];
                        CFG.priceOverrides = Object.fromEntries(
                            priceRows
                                .filter(row => row && row.day && Number.isFinite(Number(row.price_override)))
                                .map(row => [row.day, Number(row.price_override)])
                        );
                    }

                    refreshPublicBasePrice();
                } catch (error) {
                    console.warn("[SARLAT MASTER] Lecture tarifs indisponible, états calendrier conservés.", error);
                    refreshPublicBasePrice();
                }
            }

            // DIGIY PUBLIC LIVE SYNC V2'''

s2, count = pattern.subn(replacement, s, count=1)
if count != 1:
    raise SystemExit('Bloc syncMasterCalendar V3 attendu introuvable : arrêt sans modification.')

path.write_text(s2, encoding='utf-8')
print('Synchronisation publique V4 : calendrier REST indépendant du SDK/CDN.')
