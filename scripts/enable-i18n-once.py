from pathlib import Path
p=Path('index.html')
s=p.read_text()
tag='<script src="i18n/sarlat-i18n.js?v=20260828-i18n-v1"></script>'
if tag in s:
    raise SystemExit('i18n already enabled')
needle='\n</body>'
if needle not in s:
    raise SystemExit('closing body not found')
s=s.replace(needle,'\n    '+tag+needle,1)
p.write_text(s)
