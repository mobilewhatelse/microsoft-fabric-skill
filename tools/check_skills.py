"""Prueft die SKILL.md-Dateien auf Portabilitaet zwischen Claude Code und GitHub Copilot (CLI, Cloud Agent, VS Code).

Erlaubt im Frontmatter sind nur die dokumentierten, gemeinsamen Felder:  name, description, license.
Weitere Felder (z. B. argument-hint, user-invocable, allowed-tools) kennt nicht jede Umgebung - Copilot meldet sie als nicht
unterstuetzt. Dazu: name = Ordnername (nur a-z, 0-9, Bindestrich, max. 64), description 10-1024 Zeichen, gueltiges YAML.

    python tools/check_skills.py
"""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"name", "description", "license"}
bad = 0
for f in sorted((ROOT / ".github" / "skills").glob("*/SKILL.md")):
    rel = f.relative_to(ROOT)
    text = f.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, flags=re.S)
    if not m:
        print(f"{rel}: kein Frontmatter"); bad += 1; continue
    fields = {}
    for ln in m.group(1).splitlines():
        if not ln.strip():
            continue
        km = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", ln)
        if not km:
            print(f"{rel}: Zeile kein 'schluessel: wert' (mehrzeilig oder Einrueckung?): {ln[:60]}"); bad += 1; continue
        fields[km.group(1)] = km.group(2).strip()
    extra = set(fields) - ALLOWED
    if extra: print(f"{rel}: nicht portable Felder: {sorted(extra)}"); bad += 1
    for req in ("name", "description"):
        if req not in fields: print(f"{rel}: Pflichtfeld '{req}' fehlt"); bad += 1
    name = fields.get("name", "")
    if name != f.parent.name: print(f"{rel}: name '{name}' != Ordner '{f.parent.name}'"); bad += 1
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64: print(f"{rel}: ungueltiger name '{name}'"); bad += 1
    d = fields.get("description", "")
    if not 10 <= len(d) <= 1024: print(f"{rel}: description {len(d)} Zeichen (erlaubt 10-1024)"); bad += 1
    if re.search(r":\s", d) or " #" in d or d[:1] in "[{&*!|>'\"%@`":
        print(f"{rel}: description nicht sicher als einfacher YAML-Text (': ', ' #' oder Sonderzeichen am Anfang) - in Anfuehrungszeichen setzen"); bad += 1
print(f"\n{bad} Problem(e)")
sys.exit(1 if bad else 0)
