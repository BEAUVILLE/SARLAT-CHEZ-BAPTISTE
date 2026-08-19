# Déclenchement séparé confirmé 2026-08-19
from pathlib import Path
import re

path = Path('index.html')
html = path.read_text(encoding='utf-8')

# Revenir au MASTER sans les deux liaisons externes ajoutées pendant les essais.
html = html.replace('    <link rel="stylesheet" href="./mobile-compact.css?v=20260802-1">\n', '', 1)
html = html.replace('    <script src="./mobile-compact.js?v=20260802-1" defer></script>\n', '', 1)

# Retirer les anciennes indisponibilités visibles.
for label in ('30 juillet 2026', '1 au 3 août 2026', '8 août 2026'):
    html = re.sub(r'^.*' + re.escape(label) + r'.*\n?', '', html, count=1, flags=re.MULTILINE)

html = html.replace('<!-- disponibilités fixes -->', '<!-- disponibilités à jour -->', 1)

# Poser le 19 août occupé et dater les périodes futures pour l'auto-nettoyage.
row_26 = '<div class="period"><span>26 au 28 août 2026</span><strong>Occupé</strong></div>'
row_26_dated = '<div class="period" data-end="2026-08-28"><span>26 au 28 août 2026</span><strong>Occupé</strong></div>'
row_19 = '<div class="period" data-end="2026-08-19"><span>19 août 2026</span><strong>Occupé</strong></div>'

if '19 août 2026' not in html:
    if row_26 not in html:
        raise SystemExit('Période 26-28 août introuvable')
    html = html.replace(row_26, row_19 + '\n                    ' + row_26_dated, 1)
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

# Remplacer les dates bloquées par l'état réel validé.
new_blocked = '''blockedDates: [
                    "2026-08-19",
                    "2026-08-26",
                    "2026-08-27",
                    "2026-08-28",
                    "2026-09-15",
                    "2026-09-16",
                    "2026-09-29"
                ]'''
html, count = re.subn(r'blockedDates:\s*\[.*?\]', new_blocked, html, count=1, flags=re.DOTALL)
if count != 1:
    raise SystemExit('blockedDates introuvable')

# Une date passée disparaît automatiquement de la liste et du blocage technique.
if 'cleanPastAvailability' not in html:
    marker = '            // ===== WHATSAPP LINKS ====='
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
        raise SystemExit('Ancre WhatsApp introuvable')
    html = html.replace(marker, cleanup + marker, 1)

# Garde-fous.
for stale in ('2026-07-30', '2026-08-01', '2026-08-02', '2026-08-03', '2026-08-08'):
    if stale in html:
        raise SystemExit('Ancienne date technique encore présente: ' + stale)
for stale_label in ('30 juillet 2026', '1 au 3 août 2026', '8 août 2026'):
    if stale_label in html:
        raise SystemExit('Ancienne date visible encore présente: ' + stale_label)
if '19 août 2026' not in html or '"2026-08-19"' not in html:
    raise SystemExit('19 août non posé')
if 'mobile-compact.css?v=20260802-1' in html or 'mobile-compact.js?v=20260802-1' in html:
    raise SystemExit('Liaison externe involontaire encore présente')

path.write_text(html, encoding='utf-8')
print('INDEX_CALENDAR_PATCH_OK')
