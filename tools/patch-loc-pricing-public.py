from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

marker = 'DIGIY PUBLIC STATE+PRICE SYNC V5'
if marker in s:
    print('Synchronisation publique V5 déjà présente.')
    raise SystemExit(0)

# 1) Le calendrier et les prix publics passent tous les deux par REST natif.
pattern = re.compile(
    r"            // ===== SYNCHRONISATION PUBLIQUE DU MASTER LOC =====\n"
    r"            // DIGIY PUBLIC STATE SYNC V4.*?\n"
    r"            async function syncMasterCalendar\(\) \{.*?\n"
    r"            \}\n\n"
    r"            // DIGIY PUBLIC LIVE SYNC V2",
    re.S,
)

replacement = '''            // ===== SYNCHRONISATION PUBLIQUE DU MASTER LOC =====
            // DIGIY PUBLIC STATE+PRICE SYNC V5 — calendrier ET tarifs lus sans dépendre du SDK/CDN Supabase.
            async function syncMasterCalendar() {
                if (!CFG.masterUnitId) return;

                const SUPABASE_URL = "https://wesqmwjjtsefyjnluosj.supabase.co";
                const PUBLIC_KEY = "sb_publishable_tGHItRgeWDmGjnd0CK1DVQ_BIep4Ug3";
                const headers = { apikey: PUBLIC_KEY, Accept: "application/json" };
                const todayIso = localIso(new Date());

                // 1) Disponibilités : source de vérité du calendrier public.
                try {
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
                    );

                    if (!response.ok) {
                        throw new Error("HTTP " + response.status + " " + (await response.text()));
                    }

                    const rows = await response.json();
                    const safeRows = Array.isArray(rows) ? rows : [];
                    CFG.blockedDates = safeRows.filter(row => row.status === "occupied").map(row => row.day);
                    CFG.closedDates = safeRows.filter(row => row.status === "closed").map(row => row.day);

                    if (window.DIGIY_RENDER_AVAILABILITY) window.DIGIY_RENDER_AVAILABILITY(safeRows);
                    if (window.DIGIY_REFRESH_PUBLIC_CALENDAR) window.DIGIY_REFRESH_PUBLIC_CALENDAR();
                } catch (error) {
                    console.warn("[SARLAT MASTER] Lecture calendrier REST indisponible, repli local conservé.", error);
                    return;
                }

                // 2) Tarifs : même route REST native, indépendante du CDN Supabase.
                try {
                    const unitParams = new URLSearchParams({
                        select: "base_price,price_currency",
                        id: "eq." + CFG.masterUnitId,
                        limit: "1"
                    });
                    const priceParams = new URLSearchParams({
                        select: "day,price_override",
                        unit_id: "eq." + CFG.masterUnitId,
                        day: "gte." + todayIso,
                        order: "day.asc"
                    });
                    priceParams.append("day", "lte." + CFG.lastDate);

                    const [unitResponse, priceResponse] = await Promise.all([
                        fetch(SUPABASE_URL + "/rest/v1/digiy_loc_master_units?" + unitParams.toString(),
                            { method: "GET", headers, cache: "no-store" }),
                        fetch(SUPABASE_URL + "/rest/v1/digiy_loc_master_unit_prices?" + priceParams.toString(),
                            { method: "GET", headers, cache: "no-store" })
                    ]);

                    if (unitResponse.ok) {
                        const unitRows = await unitResponse.json();
                        const unit = Array.isArray(unitRows) ? unitRows[0] : null;
                        const liveBase = Number(unit && unit.base_price);
                        if (Number.isFinite(liveBase) && liveBase >= 0) CFG.eur = liveBase;
                    } else {
                        console.warn("[SARLAT MASTER] Prix de base REST indisponible : HTTP", unitResponse.status);
                    }

                    if (priceResponse.ok) {
                        const priceRowsRaw = await priceResponse.json();
                        const priceRows = Array.isArray(priceRowsRaw) ? priceRowsRaw : [];
                        CFG.priceOverrides = Object.fromEntries(
                            priceRows
                                .filter(row => row && row.day && Number.isFinite(Number(row.price_override)))
                                .map(row => [row.day, Number(row.price_override)])
                        );
                    } else {
                        console.warn("[SARLAT MASTER] Tarifs jour REST indisponibles : HTTP", priceResponse.status);
                    }

                    refreshPublicBasePrice();
                    if (window.DIGIY_REFRESH_PUBLIC_CALENDAR) window.DIGIY_REFRESH_PUBLIC_CALENDAR();
                } catch (error) {
                    console.warn("[SARLAT MASTER] Lecture tarifs REST indisponible, prix de base local conservé.", error);
                    refreshPublicBasePrice();
                }
            }

            // DIGIY PUBLIC LIVE SYNC V2'''

s2, count = pattern.subn(replacement, s, count=1)
if count != 1:
    raise SystemExit('Bloc syncMasterCalendar V4 attendu introuvable : arrêt sans modification.')
s = s2

# 2) Afficher le prix dans chaque date réellement disponible du calendrier.
old_render = '''                        html += `<div class="${cls}" data-date="${iso(date)}">${d}</div>`;'''
new_render = '''                        const dateIso = iso(date);
                        const priceHtml = !disabled
                            ? `<small class="day-price">${eurText(priceForIso(dateIso))}</small>`
                            : "";
                        html += `<div class="${cls}" data-date="${dateIso}"><span class="day-number">${d}</span>${priceHtml}</div>`;'''
if old_render not in s:
    raise SystemExit('Rendu des cases calendrier attendu introuvable : arrêt sans modification.')
s = s.replace(old_render, new_render, 1)

# 3) Donner assez de place au numéro + tarif, sans casser la grille mobile.
old_css = '''        .calendar-grid .day {
            padding: 6px 0;
            border-radius: 999px;
            cursor: pointer;
            font-weight: 800;
            font-size: 14px;'''
new_css = '''        .calendar-grid .day {
            min-height: 48px;
            padding: 5px 0;
            border-radius: 18px;
            cursor: pointer;
            font-weight: 800;
            font-size: 14px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 2px;
            line-height: 1.05;'''
if old_css not in s:
    raise SystemExit('CSS calendrier attendu introuvable : arrêt sans modification.')
s = s.replace(old_css, new_css, 1)

anchor = '''        .calendar-grid .day:hover:not(.disabled):not(.blocked) {'''
price_css = '''        .calendar-grid .day-price {
            display: block;
            font-size: 9px;
            line-height: 1;
            font-weight: 1000;
            color: #315b43;
            white-space: nowrap;
        }
        .calendar-grid .day.selected-start .day-price,
        .calendar-grid .day.selected-end .day-price {
            color: #fff;
        }
'''
if anchor not in s:
    raise SystemExit('Ancre CSS prix calendrier introuvable : arrêt sans modification.')
s = s.replace(anchor, price_css + anchor, 1)

path.write_text(s, encoding='utf-8')
print('V5 posée : disponibilités + tarifs via REST, prix visibles dans les dates disponibles.')
