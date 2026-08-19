from pathlib import Path
import re

path = Path("index.html")
html = path.read_text(encoding="utf-8")

# 1) Nettoyer les anciennes indisponibilités visibles.
for label in ("30 juillet 2026", "1 au 3 août 2026", "8 août 2026"):
    html = re.sub(r"^.*" + re.escape(label) + r".*\n?", "", html, count=1, flags=re.MULTILINE)

# 2) Mettre à jour le bloc visible sans dépendre de l'indentation.
html = html.replace("<!-- disponibilités fixes -->", "<!-- disponibilités à jour -->", 1)

row_26 = '<div class="period"><span>26 au 28 août 2026</span><strong>Occupé</strong></div>'
row_26_dated = '<div class="period" data-end="2026-08-28"><span>26 au 28 août 2026</span><strong>Occupé</strong></div>'
row_19 = '<div class="period" data-end="2026-08-19"><span>19 août 2026</span><strong>Occupé</strong></div>'

if "19 août 2026" not in html:
    if row_26 in html:
        html = html.replace(row_26, row_19 + "\n                    " + row_26_dated, 1)
    elif row_26_dated in html:
        html = html.replace(row_26_dated, row_19 + "\n                    " + row_26_dated, 1)
else:
    html = html.replace(row_26, row_26_dated, 1)

html = html.replace(
    '<div class="period"><span>15 et 16 septembre 2026</span><strong>Occupé</strong></div>',
    '<div class="period" data-end="2026-09-16"><span>15 et 16 septembre 2026</span><strong>Occupé</strong></div>',
    1,
)
html = html.replace(
    '<div class="period"><span>29 septembre 2026</span><strong>Occupé</strong></div>',
    '<div class="period" data-end="2026-09-29"><span>29 septembre 2026</span><strong>Occupé</strong></div>',
    1,
)

# 3) Remplacer la liste technique des dates occupées.
new_blocked = '''blockedDates: [
                    "2026-08-19",
                    "2026-08-26",
                    "2026-08-27",
                    "2026-08-28",
                    "2026-09-15",
                    "2026-09-16",
                    "2026-09-29"
                ]'''
html, count = re.subn(
    r"blockedDates:\s*\[.*?\]",
    new_blocked,
    html,
    count=1,
    flags=re.DOTALL,
)
if count != 1:
    raise SystemExit("blockedDates introuvable")

# 4) Nettoyage automatique côté navigateur : une indisponibilité passée disparaît.
if "cleanPastAvailability" not in html:
    marker = "            // ===== WHATSAPP LINKS ====="
    cleanup = '''            // Nettoyage automatique des indisponibilités passées.
            (function cleanPastAvailability() {
                const now = new Date();
                const todayISO = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" + String(now.getDate()).padStart(2, "0");
                CFG.blockedDates = CFG.blockedDates.filter(date => date >= todayISO);
                document.querySelectorAll(".availability .period[data-end]").forEach(row => {
                    if (row.dataset.end < todayISO) row.remove();
                });
            })();

'''
    if marker not in html:
        raise SystemExit("Ancre WhatsApp introuvable")
    html = html.replace(marker, cleanup + marker, 1)

# 5) Garde-fous finaux.
for stale in ("2026-07-30", "2026-08-01", "2026-08-02", "2026-08-03", "2026-08-08"):
    if stale in html:
        raise SystemExit("Ancienne date technique encore présente: " + stale)

for stale_label in ("30 juillet 2026", "1 au 3 août 2026", "8 août 2026"):
    if stale_label in html:
        raise SystemExit("Ancienne date visible encore présente: " + stale_label)

if "19 août 2026" not in html or '"2026-08-19"' not in html:
    raise SystemExit("Le 19 août occupé n'a pas été posé")

path.write_text(html, encoding="utf-8")
print("CALENDAR_PATCH_OK")
