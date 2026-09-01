from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

marker = 'DIGIY PUBLIC STATE SYNC V3'
if marker in s:
    print('Synchronisation publique des états déjà découplée des tarifs.')
    raise SystemExit(0)

pattern = re.compile(
    r"            // ===== SYNCHRONISATION PUBLIQUE DU MASTER LOC =====\n"
    r"            async function syncMasterCalendar\(\) \{.*?\n"
    r"            \}\n\n"
    r"            // DIGIY PUBLIC LIVE SYNC V2",
    re.S,
)

replacement = '''            // ===== SYNCHRONISATION PUBLIQUE DU MASTER LOC =====
            // DIGIY PUBLIC STATE SYNC V3 — disponibilités prioritaires, tarifs indépendants.
            async function syncMasterCalendar() {
                if (!window.supabase || !CFG.masterUnitId) return;

                const publicDb = window.supabase.createClient(
                    "https://wesqmwjjtsefyjnluosj.supabase.co",
                    "sb_publishable_tGHItRgeWDmGjnd0CK1DVQ_BIep4Ug3",
                    {
                        auth: {
                            persistSession: false,
                            autoRefreshToken: false,
                            detectSessionInUrl: false
                        }
                    }
                );

                const todayIso = localIso(new Date());

                // 1) PRIORITÉ ABSOLUE : relire les états calendrier et les rendre immédiatement.
                try {
                    const calendarResult = await publicDb
                        .from("digiy_loc_master_unit_calendar")
                        .select("day,status")
                        .eq("unit_id", CFG.masterUnitId)
                        .gte("day", todayIso)
                        .lte("day", CFG.lastDate)
                        .order("day");

                    if (calendarResult.error) throw calendarResult.error;

                    const rows = Array.isArray(calendarResult.data) ? calendarResult.data : [];
                    CFG.blockedDates = rows.filter(row => row.status === "occupied").map(row => row.day);
                    CFG.closedDates = rows.filter(row => row.status === "closed").map(row => row.day);

                    if (window.DIGIY_RENDER_AVAILABILITY) {
                        window.DIGIY_RENDER_AVAILABILITY(rows);
                    }
                    if (window.DIGIY_REFRESH_PUBLIC_CALENDAR) {
                        window.DIGIY_REFRESH_PUBLIC_CALENDAR();
                    }
                } catch (error) {
                    console.warn("[SARLAT MASTER] Lecture calendrier indisponible, repli local conservé.", error);
                    return;
                }

                // 2) Tarifs en lecture séparée : un problème tarifaire ne bloque jamais les états.
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
    raise SystemExit('Bloc syncMasterCalendar attendu introuvable : arrêt sans modification.')

path.write_text(s2, encoding='utf-8')
print('Synchronisation publique : états calendrier indépendants des tarifs.')
