from pathlib import Path
p=Path('index.html')
s=p.read_text()
old='style="grid-column:1/-1;flex:1 1 100%;width:100%;min-height:52px;display:inline-flex;align-items:center;justify-content:center;gap:9px;padding:11px 18px;border:2px solid #c99743;border-radius:999px;background:#315b43;color:#fff;text-decoration:none;font-size:15px;font-weight:1000;letter-spacing:.02em;box-shadow:0 8px 20px rgba(49,91,67,.22)"'
new='style="flex:0 0 auto;width:auto;min-height:42px;display:inline-flex;align-items:center;justify-content:flex-start;gap:6px;padding:8px 12px;border:2px solid #c99743;border-radius:999px;background:#315b43;color:#fff;text-decoration:none;font-size:12px;font-weight:1000;letter-spacing:.01em;box-shadow:0 6px 16px rgba(49,91,67,.18);justify-self:start"'
if old not in s: raise SystemExit('return style not found')
s=s.replace(old,new,1)
p.write_text(s)
