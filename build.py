#!/usr/bin/env python3
"""Build guidebook DOC*.md into a standalone static site. Stdlib only.

Usage: python build.py
Output: out/*.html (preview) + docs/*.html (GitHub Pages).
Publish with: git add . && git commit -m ... && git push
"""
import html
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "out")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

DOCS = [
    ("DOC1-practical-short.md", "Practical Short — Student Guide"),
    ("DOC2-detailed-long.md", "Detailed Long — Evidence Report"),
    ("DOC3-mix-textbook.md", "Mix Textbook — Teacher Lessons"),
]


def esc(s):
    return html.escape(s or "", quote=True)


def shell(title, body_inner):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{{background:#f7f7f5;color:#1a1a1a;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0}}
.wrap{{max-width:880px;margin:0 auto;padding:24px 16px 64px}}
.topbar{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
.topbar a{{color:#555;text-decoration:none;font-size:14px}}
.card{{background:#fff;border:1px solid #e7e5e4;border-radius:12px;padding:16px;margin:12px 0}}
.tldr{{background:#fff;border:1px solid #e7e5e4;border-left:4px solid #1a1a1a;border-radius:12px;padding:16px;margin:16px 0}}
.badge{{display:inline-block;background:#f1f0ee;border-radius:999px;padding:2px 10px;font-size:12px;margin-right:6px}}
.muted{{color:#6b7280;font-size:13px}}
.grid2{{display:grid;grid-template-columns:1fr;gap:0}}
@media(min-width:720px){{.grid2{{grid-template-columns:1fr 1fr;gap:12px}}.grid2 .card{{margin:0}}}}
.sec{{margin-top:28px}}
a{{color:#0f62fe}}
h1{{font-size:26px;margin:8px 0}}h2{{font-size:19px;margin:0 0 8px}}h3{{font-size:16px;margin:14px 0 6px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid #e7e5e4;vertical-align:top}}
th{{background:#f7f7f5;font-weight:600}}
.placeholder{{border:1.5px dashed #a8a29e;border-radius:12px;padding:14px 16px;margin:12px 0;background:#fafaf9;color:#57534e;font-size:14px;list-style:none}}
.toc{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px;position:sticky;top:0;z-index:5;background:#f7f7f5;padding:8px 0}}
.hero{{text-align:center}}
.hero h1{{font-size:30px}}
.chapter{{background:#fff;border:1px solid #e7e5e4;border-radius:14px;padding:4px 20px 16px;margin:20px 0}}
.chapter h2{{margin-top:14px}}
.toc a{{background:#fff;border:1px solid #e7e5e4;border-radius:999px;padding:4px 12px;font-size:13px;color:#1a1a1a;text-decoration:none}}
@media(min-width:1100px){{.wrap{{max-width:1100px}}.grid2{{grid-template-columns:1fr 1fr 1fr}}}}
@media print{{.topbar{{display:none}}.toc{{position:static;background:#fff}}.wrap{{max-width:100%;padding:0}}body{{background:#fff}}.card,.tldr{{break-inside:avoid}}}}
</style>
</head>
<body>
<div class="wrap mx-auto px-4">
<div class="topbar"><a href="index.html">&larr; Alph</a><span class="muted">Guidebook</span></div>
{body_inner}
</div>
</body>
</html>"""


def inline(s):
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", s)
    return s


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def md_to_html(text):
    out, toc, seen, lines, i = [], [], set(), text.split("\n"), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:])}</h3>")
        elif ln.startswith("## "):
            sid = slug(ln[3:]) or "sec"
            base, n = sid, 1
            while sid in seen:
                n += 1
                sid = f"{base}-{n}"
            seen.add(sid)
            toc.append((sid, ln[3:].strip()))
            out.append(f'<h2 id="{sid}">{inline(ln[3:])}</h2>')
        elif ln.startswith("# "):
            out.append(f"<h1>{inline(ln[2:])}</h1>")
        elif ln.strip() == "---":
            i += 1  # dropped: chapter cards give the separation now
            continue
        elif ln.startswith("> "):
            quotes = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quotes.append(inline(lines[i].strip()[2:]))
                i += 1
            out.append('<div class="tldr">' + "<br>".join(quotes) + "</div>")
            continue
        elif ln.strip().startswith("|"):
            tbl, hdr = ["<div class='card'><table>"], True
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if all(c and set(c) <= set("-: ") for c in raw):
                    i += 1
                    continue
                cells = [inline(c) for c in raw]
                tag = "th" if hdr else "td"
                tbl.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
                hdr, i = False, i + 1
            tbl.append("</table></div>")
            out.append("\n".join(tbl))
            continue
        elif ln.startswith(("- ", "* ")):
            items = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                txt = lines[i].strip()[2:].strip()
                if txt.lower().startswith(("[graph", "[picture", "[qr", "[image")):
                    items.append(f'<li class="placeholder">{inline(txt)}</li>')
                else:
                    items.append(f"<li>{inline(txt)}</li>")
                i += 1
            out.append("<ul class='card'>" + "\n".join(items) + "</ul>")
            continue
        elif re.match(r"\d+\. ", ln.strip()):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i].strip()):
                txt = re.sub(r"^\d+\.\s*", "", lines[i].strip())
                if txt.lower().startswith(("[graph", "[picture", "[qr", "[image")):
                    items.append(f'<li class="placeholder">{inline(txt)}</li>')
                else:
                    items.append(f"<li>{inline(txt)}</li>")
                i += 1
            out.append("<ol class='card'>" + "\n".join(items) + "</ol>")
            continue
        else:
            txt = ln.strip()
            if txt.lower().startswith(("[graph", "[picture", "[qr", "[image")):
                out.append(f'<div class="placeholder">{inline(txt)}</div>')
            else:
                out.append(f"<p>{inline(txt)}</p>")
        i += 1
    hero, rest = group_sections(out)
    if toc:
        nav = '<div class="toc">' + "".join(
            f'<a href="#{esc(sid)}">{esc(t)}</a>' for sid, t in toc
        ) + "</div>"
        return hero + nav + rest
    return hero + rest


def group_sections(blocks):
    """Cover blocks -> hero card; each h2 + following blocks -> chapter card."""
    idx = [n for n, b in enumerate(blocks) if b.startswith("<h2")]
    if not idx:
        return "", "\n".join(blocks)
    hero = ""
    if idx[0] > 0:
        hero = '<div class="hero card">\n' + "\n".join(blocks[:idx[0]]) + "\n</div>\n"
    rest = []
    for k, s in enumerate(idx):
        e = idx[k + 1] if k + 1 < len(idx) else len(blocks)
        rest.append('<section class="chapter">\n' + "\n".join(blocks[s:e]) + "\n</section>")
    return hero, "\n".join(rest)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    for fn, label in DOCS:
        with open(os.path.join(BASE_DIR, fn), encoding="utf-8") as f:
            html = shell(label, md_to_html(f.read()))
        name = fn.replace(".md", ".html")
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
            f.write(html)
        shutil.copy(os.path.join(OUT_DIR, name), os.path.join(DOCS_DIR, name))
        print(f"Built: {name}")
    idx_body = "<h1>Guidebook</h1>" + "".join(
        f'<div class="card"><a href="{fn.replace(".md", ".html")}"><b>{esc(label)}</b></a></div>'
        for fn, label in DOCS
    )
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(shell("Guidebook", idx_body))
    shutil.copy(os.path.join(OUT_DIR, "index.html"), os.path.join(DOCS_DIR, "index.html"))
    print("Built: index.html (out/ + docs/)")


if __name__ == "__main__":
    main()
