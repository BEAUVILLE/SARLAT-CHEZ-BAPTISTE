from pathlib import Path
import re

path = Path("index.html")
s = path.read_text(encoding="utf-8")

MARKER = "DIGIY PUBLIC LOC SYNC V1"
if MARKER in s:
    print("Public LOC sync already patched")
    raise SystemExit(0)

# 1) Make the three visible base-price labels addressable.
replacements = [
    (
        '<div class="price-block-hero">\n                        <strong>78 € / nuitée</strong>\n                        <span>≈ 51 165 FCFA</span>\n                    </div>',
        '<div class="price-block-hero">\n                        <strong id="publicHeroPrice">78 € / nuitée</strong>\n                        <span id="publicHeroPriceXof">≈ 51 165 FCFA</span>\n                    </div>'
    ),
    (
        '<div class="estimate full" id="estimate">\n                            <strong>78 € / nuitée</strong>\n                            <span>≈ 51 165 FCFA · choisissez vos dates.</span>\n                        </div>',
        '<div class="estimate full" id="estimate">\n                            <strong>78 € / nuitée</strong>\n                            <span>≈ 51 165 FCFA · choisissez vos dates.</span>\n                        </div>'
    ),
    (
        '<li>✓ 78 € ≈ 51 165 FCFA / nuitée</li>',
        '<li id="publicSummaryPrice">✓ 78 € ≈ 51 165 FCFA / nuitée</li>'
    ),
]
for old, new in replacements:
    if old not in s:
        raise SystemExit(f"Expected markup anchor missing: {old[:80]}")
    s = s.replace(old, new, 1)

# 2) Extend runtime pricing config.
old_cfg = '''                eur: 78,\n                xof: 51165,\n                lastDate: "2026-10-30",'''
new_cfg = '''                eur: 78,\n                xof: 51165,\n                eurToXof: 655.957,\n                priceOverrides: {},\n                lastDate: "2026-10-30",'''
if old_cfg not in s:
    raise SystemExit("CFG pricing anchor missing")
s = s.replace(old_cfg, new_cfg, 1)

# 3) Add shared public pricing helpers before availability functions.
anchor = "            // ===== DISPONIBILITÉS VISIBLES — MASTER SUPABASE + REPLI LOCAL ====="
helpers = r'''            // DIGIY PUBLIC LOC SYNC V1
            function locIsoDate(date) {
                return date.getFullYear() + "-" + String(date.getMonth() + 1).padStart(2, "0") + "-" + String(date.getDate()).padStart(2, "0");
            }

            function priceForIso(day) {
                const hasOverride = CFG.priceOverrides && Object.prototype.hasOwnProperty.call(CFG.priceOverrides, day);
                const value = hasOverride ? Number(CFG.priceOverrides[day]) : Number(CFG.eur);
                return Number.isFinite(value) && value >= 0 ? value : Number(CFG.eur) || 0;
            }

            function stayTotalEUR(arrivalIso, departureIso) {
                if (!arrivalIso || !departureIso) return 0;
                const cursor = new Date(arrivalIso + "T12:00:00");
                const departure = new Date(departureIso + "T12:00:00");
                if (!Number.isFinite(cursor.getTime()) || !Number.isFinite(departure.getTime()) || cursor >= departure) return 0;
                let total = 0;
                while (cursor < departure) {
                    total += priceForIso(locIsoDate(cursor));
                    cursor.setDate(cursor.getDate() + 1);
                }
                return total;
            }

            function eurText(value) {
                const n = Number(value) || 0;
                return n.toLocaleString("fr-FR", { minimumFractionDigits: Number.isInteger(n) ? 0 : 2, maximumFractionDigits: 2 }) + " €";
            }

            function xofFromEur(value) {
                return Math.round((Number(value) || 0) * CFG.eurToXof);
            }

            function refreshPublicBasePrice() {
                const base = Number(CFG.eur) || 0;
                const xof = xofFromEur(base);
                CFG.xof = xof;
                const hero = document.getElementById("publicHeroPrice");
                const heroXof = document.getElementById("publicHeroPriceXof");
                const summary = document.getElementById("publicSummaryPrice");
                if (hero) hero.textContent = eurText(base) + " / nuitée";
                if (heroXof) heroXof.textContent = "≈ " + xof.toLocaleString("fr-FR") + " FCFA";
                if (summary) summary.textContent = "✓ " + eurText(base) + " ≈ " + xof.toLocaleString("fr-FR") + " FCFA / nuitée";
            }

'''
if anchor not in s:
    raise SystemExit("Availability anchor missing")
s = s.replace(anchor, helpers + anchor, 1)

# 4) Replace the public selection estimate so it sums each night's effective price.
pattern = re.compile(r'''                function updateDisplay\(\) \{.*?\n                \}\n\n                function renderCalendar\(\) \{''', re.S)
replacement = r'''                function updateDisplay() {
                    const n = nights();
                    if (start && end && n > 0) {
                        dateRange.textContent = "📅 " + formatDate(start) + " → " + formatDate(end);
                        nightsDisplay.textContent = "🛏️ " + plural(n, "nuit", "nuits");
                        const startIso = iso(start);
                        const endIso = iso(end);
                        const totalEur = stayTotalEUR(startIso, endIso);
                        const totalXof = xofFromEur(totalEur);
                        estimateEl.innerHTML =
                            `<strong>${n} nuitée${n > 1 ? "s" : ""} : ${eurText(totalEur)}</strong><span>≈ ${totalXof.toLocaleString("fr-FR")} FCFA · tarifs synchronisés</span>`;
                        if (arrivalInput) arrivalInput.value = startIso;
                        if (departureInput) departureInput.value = endIso;
                    } else {
                        dateRange.textContent = "📅 Sélectionnez vos dates";
                        nightsDisplay.textContent = "🛏️ —";
                        const baseXof = xofFromEur(CFG.eur);
                        estimateEl.innerHTML =
                            `<strong>${eurText(CFG.eur)} / nuitée</strong><span>≈ ${baseXof.toLocaleString("fr-FR")} FCFA · choisissez vos dates.</span>`;
                    }
                }

                function renderCalendar() {'''
s, count = pattern.subn(replacement, s, count=1)
if count != 1:
    raise SystemExit("updateDisplay function anchor missing")

# 5) Replace public master sync: status + base price + per-day price overrides.
sync_pattern = re.compile(r'''            // ===== SYNCHRONISATION PUBLIQUE DU MASTER LOC =====.*?\n            // ===== FORMULAIRE =====''', re.S)
sync_replacement = r'''            // ===== SYNCHRONISATION PUBLIQUE DU MASTER LOC =====
            (async function syncMasterCalendar() {
                if (!window.supabase || !CFG.masterUnitId) return;

                try {
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
                    const [calendarResult, unitResult, priceResult] = await Promise.all([
                        publicDb
                            .from("digiy_loc_master_unit_calendar")
                            .select("day,status")
                            .eq("unit_id", CFG.masterUnitId)
                            .gte("day", todayIso)
                            .lte("day", CFG.lastDate)
                            .order("day"),
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

                    if (calendarResult.error) throw calendarResult.error;
                    if (unitResult.error) throw unitResult.error;
                    if (priceResult.error) throw priceResult.error;

                    const rows = Array.isArray(calendarResult.data) ? calendarResult.data : [];
                    const priceRows = Array.isArray(priceResult.data) ? priceResult.data : [];
                    const liveBase = Number(unitResult.data && unitResult.data.base_price);
                    if (Number.isFinite(liveBase) && liveBase >= 0) CFG.eur = liveBase;
                    CFG.priceOverrides = Object.fromEntries(
                        priceRows
                            .filter(row => row && row.day && Number.isFinite(Number(row.price_override)))
                            .map(row => [row.day, Number(row.price_override)])
                    );

                    CFG.blockedDates = rows.filter(row => row.status === "occupied").map(row => row.day);
                    CFG.closedDates = rows.filter(row => row.status === "closed").map(row => row.day);
                    refreshPublicBasePrice();

                    if (window.DIGIY_RENDER_AVAILABILITY) {
                        window.DIGIY_RENDER_AVAILABILITY(rows);
                    }
                    if (window.DIGIY_REFRESH_PUBLIC_CALENDAR) {
                        window.DIGIY_REFRESH_PUBLIC_CALENDAR();
                    }
                } catch (error) {
                    console.warn("[SARLAT MASTER] Lecture Supabase indisponible, repli local conservé.", error);
                    refreshPublicBasePrice();
                }
            })();

            // ===== FORMULAIRE ====='''
s, count = sync_pattern.subn(sync_replacement, s, count=1)
if count != 1:
    raise SystemExit("syncMasterCalendar block anchor missing")

# 6) Make WhatsApp/email estimate use the exact synchronized stay total.
old_after_nights = '''                    const n = Math.round((new Date(d + "T12:00") - new Date(a + "T12:00")) / 86400000);\n                    if (n <= 0) throw new Error("La date de départ doit être après l'arrivée.");\n\n                    return ['''
new_after_nights = '''                    const n = Math.round((new Date(d + "T12:00") - new Date(a + "T12:00")) / 86400000);\n                    if (n <= 0) throw new Error("La date de départ doit être après l'arrivée.");\n                    const totalEur = stayTotalEUR(a, d);\n                    const totalXof = xofFromEur(totalEur);\n\n                    return ['''
if old_after_nights not in s:
    raise SystemExit("buildMessage nights anchor missing")
s = s.replace(old_after_nights, new_after_nights, 1)

old_estimate_line = '''                        "Estimation : " + (n * 78).toLocaleString("fr-FR") + " € / " + (n * 51165).toLocaleString(\n                        "fr-FR") + " FCFA",'''
new_estimate_line = '''                        "Estimation : " + eurText(totalEur) + " / " + totalXof.toLocaleString("fr-FR") + " FCFA",'''
if old_estimate_line not in s:
    raise SystemExit("buildMessage fixed estimate anchor missing")
s = s.replace(old_estimate_line, new_estimate_line, 1)

path.write_text(s, encoding="utf-8")
print("Public LOC availability + pricing synchronization patched")
