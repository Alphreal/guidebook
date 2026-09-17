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
    ("DOC1-practical-short.md", "Practical Short — Student Guide",
     "Routines first: 5-minute fixes for time, distraction, interaction and fatigue."),
    ("DOC2-detailed-long.md", "Detailed Long — Evidence Report",
     "Survey results, theories and linked recommendations (n=40)."),
    ("DOC3-mix-textbook.md", "Mix Textbook — Teacher Lessons",
     "15-minute lesson scripts, activities and class norms."),
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
body{{background:#f7f7f5;color:#1a1a1a;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;line-height:1.65}}
p{{margin:10px 0}}
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
.pic{{margin:12px 0;text-align:center}}
.pic svg{{max-width:100%;height:auto;background:#fff;border:1px solid #e7e5e4;border-radius:12px}}
.pic figcaption,.pic .cap{{color:#57534e;font-size:13px;margin-top:6px}}
li.pic{{list-style:none}}
.toc{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px;position:sticky;top:0;z-index:5;background:#f7f7f5;padding:8px 0}}
.hero{{text-align:center}}
.hero h1{{font-size:30px}}
.chapter{{background:#fff;border:1px solid #e7e5e4;border-radius:14px;padding:4px 20px 16px;margin:20px 0}}
.chapter h2{{margin-top:14px}}
.toc a{{background:#fff;border:1px solid #e7e5e4;border-radius:999px;padding:4px 12px;font-size:13px;color:#1a1a1a;text-decoration:none;transition:background .15s}}
.toc a:hover{{background:#1a1a1a;color:#fff;border-color:#1a1a1a}}
.card,ul.card,ol.card{{line-height:1.7}}
ul.card,ol.card{{box-shadow:0 1px 3px rgba(0,0,0,.05)}}
.chapter{{box-shadow:0 1px 4px rgba(0,0,0,.06);border-top:3px solid #0f62fe}}
.hero{{background:linear-gradient(180deg,#ffffff,#f1efe9);box-shadow:0 1px 4px rgba(0,0,0,.06)}}
.pic svg{{box-shadow:0 1px 4px rgba(0,0,0,.08)}}
.sub{{color:#57534e;font-size:14px;margin:2px 0 0}}
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


SVG_TIMER = """<svg viewBox="0 0 400 240" role="img" aria-label="Desk timer and checklist"><rect x="20" y="212" width="360" height="8" rx="4" fill="#e7e5e4"/><circle cx="115" cy="112" r="58" fill="#fff" stroke="#1a1a1a" stroke-width="4"/><circle cx="115" cy="112" r="6" fill="#1a1a1a"/><line x1="115" y1="112" x2="115" y2="70" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/><line x1="115" y1="112" x2="145" y2="126" stroke="#0f62fe" stroke-width="4" stroke-linecap="round"/><text x="115" y="198" text-anchor="middle" font-size="16" font-weight="bold" fill="#1a1a1a">25:00</text><rect x="215" y="42" width="155" height="140" rx="10" fill="#fff" stroke="#1a1a1a" stroke-width="3"/><rect x="231" y="62" width="16" height="16" rx="3" fill="none" stroke="#1a1a1a" stroke-width="2"/><polyline points="233,70 238,75 246,65" fill="none" stroke="#0f62fe" stroke-width="3"/><text x="255" y="75" font-size="13" fill="#1a1a1a">LMS quiz</text><rect x="231" y="98" width="16" height="16" rx="3" fill="none" stroke="#1a1a1a" stroke-width="2"/><polyline points="233,106 238,111 246,101" fill="none" stroke="#0f62fe" stroke-width="3"/><text x="255" y="111" font-size="13" fill="#1a1a1a">Videos</text><rect x="231" y="134" width="16" height="16" rx="3" fill="none" stroke="#a8a29e" stroke-width="2"/><text x="255" y="147" font-size="13" fill="#57534e">Review</text></svg>"""

SVG_PHONE = """<svg viewBox="0 0 400 240" role="img" aria-label="Phone in drawer versus on desk"><text x="100" y="30" text-anchor="middle" font-size="14" font-weight="bold" fill="#1a1a1a">IN DRAWER</text><rect x="40" y="55" width="120" height="105" rx="10" fill="#f7f7f5" stroke="#1a1a1a" stroke-width="3"/><rect x="72" y="72" width="56" height="88" rx="8" fill="#1a1a1a"/><rect x="79" y="82" width="42" height="60" rx="4" fill="#57534e"/><text x="100" y="200" text-anchor="middle" font-size="30" font-weight="bold" fill="#0f62fe">✓</text><text x="300" y="30" text-anchor="middle" font-size="14" font-weight="bold" fill="#1a1a1a">ON DESK</text><rect x="240" y="152" width="120" height="8" rx="4" fill="#e7e5e4"/><rect x="283" y="82" width="44" height="70" rx="6" fill="#fff" stroke="#1a1a1a" stroke-width="3"/><path d="M270 70 Q260 100 268 130" fill="none" stroke="#a8a29e" stroke-width="2"/><path d="M340 70 Q350 100 342 130" fill="none" stroke="#a8a29e" stroke-width="2"/><text x="300" y="200" text-anchor="middle" font-size="30" font-weight="bold" fill="#57534e">✗</text></svg>"""

SVG_CHAT = """<svg viewBox="0 0 400 250" role="img" aria-label="Good help post example"><rect x="30" y="12" width="340" height="226" rx="12" fill="#fff" stroke="#1a1a1a" stroke-width="3"/><text x="48" y="40" font-size="14" font-weight="bold" fill="#1a1a1a">Class channel</text><line x1="30" y1="52" x2="370" y2="52" stroke="#e7e5e4" stroke-width="2"/><rect x="46" y="64" width="252" height="96" rx="10" fill="#f1f0ee"/><text x="60" y="90" font-size="12" fill="#1a1a1a">Tried: Unit 3 quiz Q5</text><text x="60" y="112" font-size="12" fill="#1a1a1a">Expected 70%, got 40%</text><text x="60" y="134" font-size="12" fill="#1a1a1a">Question: which formula?</text><rect x="140" y="170" width="214" height="56" rx="10" fill="#0f62fe"/><text x="156" y="193" font-size="12" fill="#fff">Good question — see</text><text x="156" y="211" font-size="12" fill="#fff">Unit 3.2, example 2</text></svg>"""

SVG_STRETCH = """<svg viewBox="0 0 400 240" role="img" aria-label="Screen distance and stretching"><rect x="36" y="66" width="124" height="84" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="3"/><rect x="48" y="78" width="100" height="60" rx="4" fill="#dbeafe"/><line x1="98" y1="150" x2="98" y2="176" stroke="#1a1a1a" stroke-width="4"/><line x1="70" y1="176" x2="126" y2="176" stroke="#1a1a1a" stroke-width="4"/><line x1="168" y1="196" x2="262" y2="196" stroke="#57534e" stroke-width="2"/><polygon points="168,196 178,191 178,201" fill="#57534e"/><polygon points="262,196 252,191 252,201" fill="#57534e"/><text x="215" y="186" text-anchor="middle" font-size="13" fill="#57534e">50 cm</text><circle cx="310" cy="60" r="14" fill="#fff" stroke="#1a1a1a" stroke-width="3"/><line x1="310" y1="74" x2="310" y2="140" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/><line x1="310" y1="92" x2="284" y2="112" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/><line x1="310" y1="92" x2="336" y2="112" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/><line x1="310" y1="140" x2="294" y2="196" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/><line x1="310" y1="140" x2="326" y2="196" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/><text x="310" y="222" text-anchor="middle" font-size="13" fill="#57534e">20-20-20</text></svg>"""

PICS = [
    (("desk timer", "timer", "checklist", "25-5"), SVG_TIMER),
    (("phone-in-drawer", "phone-on-desk", "phone in drawer", "phone on desk", "drawer", "phone"), SVG_PHONE),
    (("chat example", "good vs vague", "help post", "class chat"), SVG_CHAT),
    (("stretch", "screen distance", "20-20-20", "fatigue"), SVG_STRETCH),
]


def pic_svg(txt):
    t = txt.lower()
    for keys, svg in PICS:
        if any(k in t for k in keys):
            return svg
    return None


def slot_kind(txt):
    """Shared classifier: pic/chart/table (render), box (honest placeholder), text."""
    low = txt.lower()
    if low.startswith(("[picture", "[image")):
        return "pic" if pic_svg(txt) else "box"
    if low.startswith("[table"):
        return "table" if table_chart(txt) else "box"
    if low.startswith(("[graph", "[qr")):
        return "chart" if graph_chart(txt) else "box"
    return "text"


def list_item(txt):
    kind = slot_kind(txt)
    if kind == "pic":
        return f'<li class="pic">{pic_svg(txt)}<div class="cap">{inline(txt)}</div></li>'
    if kind == "chart":
        return f'<li class="pic">{graph_chart(txt)}<div class="cap">{inline(txt)} · real survey data</div></li>'
    if kind == "table":
        return f"<li>{table_chart(txt)}</li>"
    if kind == "box":
        return f'<li class="placeholder">{inline(txt)}</li>'
    return f"<li>{inline(txt)}</li>"


def hbars(title, rows, note=""):
    """Horizontal SVG bar chart. rows: [(label, value)]. Values shown as-is."""
    top, bh, gap = 46, 22, 12
    H = top + len(rows) * (bh + gap) + (30 if note else 14)
    maxv = max((v for _, v in rows), default=1) or 1
    p = [f'<svg viewBox="0 0 400 {H}" role="img" aria-label="{esc(title)}">',
         f'<text x="8" y="22" font-size="14" font-weight="bold" fill="#1a1a1a">{esc(title)}</text>']
    y = top
    for lab, v in rows:
        w = 150 * v / maxv
        num = f"{v:.2f}" if isinstance(v, float) else f"{v:d}"
        p.append(f'<text x="8" y="{y + 15}" font-size="12" fill="#1a1a1a">{esc(lab)}</text>')
        p.append(f'<rect x="150" y="{y}" width="150" height="{bh}" rx="5" fill="#e7e5e4"/>')
        p.append(f'<rect x="150" y="{y}" width="{w:.0f}" height="{bh}" rx="5" fill="#0f62fe"/>')
        p.append(f'<text x="{165 + w:.0f}" y="{y + 15}" font-size="12" fill="#57534e">{num}</text>')
        y += bh + gap
    if note:
        p.append(f'<text x="8" y="{H - 10}" font-size="11" fill="#57534e">{esc(note)}</text>')
    p.append("</svg>")
    return "".join(p)


# Real Week-1 survey aggregates (n=40). % agree = score 4–5/5.
BARRIERS = [("Screen / Zoom fatigue", 55), ("Distracted by apps", 53),
            ("Self-discipline", 40), ("Asking harder", 25)]

GRAPH_CHARTS = [  # most-specific keys first: first match wins
    (("discipline difficulty",), ("Self-discipline difficulty", [("Score 4-5", 40)], "40% of n=40 · comparison arm not surveyed")),
    (("distraction level",), ("Distraction by apps", [("Score 4-5", 53)], "53% of n=40 · comparison arm not surveyed")),
    (("asking difficulty",), ("Asking harder online", [("Score 4-5", 25)], "25% of n=40 · comparison arm not surveyed")),
    (("fatigue level",), ("Screen / Zoom fatigue", [("Score 4-5", 55)], "55% of n=40 · comparison arm not surveyed")),
    (("barriers by agree",), ("Barriers by agree % (4-5/5)", BARRIERS, "Week-1 survey, n=40")),
    (("graph 1", "sessions per week"), ("Online frequency (sessions/week)", [("2-4 / week", 43), ("Course-dependent", 40), ("6+ / week", 8), ("4-6 / week", 5), ("1 / week", 5)], "Options as surveyed · % rounded, sums to 101%")),
    (("graph 2", "barrier ranking"), ("Barrier ranking (agree %)", BARRIERS, "Week-1 survey, n=40")),
    (("graph 3", "perceived benefits", "likert averages"), ("Benefits (Likert avg, 1-5)", [("Remember all content", 3.5), ("Prefer online", 3.0)], "Remember avg 3.50 (55% agree) · Prefer avg 3.00 (28% agree), n=40")),
]


def graph_chart(txt):
    """SVG chart HTML or None. Never invents data: unmapped slots stay placeholders."""
    t = txt.lower()
    for keys, (title, rows, note) in GRAPH_CHARTS:
        if any(k in t for k in keys):
            return hbars(title, rows, note)
    return None


THEMES = [("Distraction, noise, social media & games", "~21"),
          ("Screen time & Zoom fatigue", "~8"),
          ("Interaction with teachers / peers", "~6"),
          ("Network, mic & devices", "~5")]


def table_chart(txt):
    if "theme" not in txt.lower():
        return None
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in THEMES)
    return ('<div class="card"><table><tr><th>Theme (primary per response)</th><th>Responses</th></tr>'
            + rows + '</table><div class="muted">Group-coded from open answers, n=40.</div></div>')


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
                items.append(list_item(lines[i].strip()[2:].strip()))
                i += 1
            out.append("<ul class='card'>" + "\n".join(items) + "</ul>")
            continue
        elif re.match(r"\d+\. ", ln.strip()):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i].strip()):
                items.append(list_item(re.sub(r"^\d+\.\s*", "", lines[i].strip())))
                i += 1
            out.append("<ol class='card'>" + "\n".join(items) + "</ol>")
            continue
        else:
            txt = ln.strip()
            kind = slot_kind(txt)
            if kind == "pic":
                out.append(f'<figure class="pic">{pic_svg(txt)}<figcaption>{inline(txt)}</figcaption></figure>')
            elif kind == "chart":
                out.append(f'<figure class="pic">{graph_chart(txt)}<figcaption>{inline(txt)} · real survey data</figcaption></figure>')
            elif kind == "table":
                out.append(table_chart(txt))
            elif kind == "box":
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
    for fn, label, _desc in DOCS:
        with open(os.path.join(BASE_DIR, fn), encoding="utf-8") as f:
            html = shell(label, md_to_html(f.read()))
        name = fn.replace(".md", ".html")
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
            f.write(html)
        shutil.copy(os.path.join(OUT_DIR, name), os.path.join(DOCS_DIR, name))
        print(f"Built: {name}")
    idx_body = "<h1>Guidebook</h1>" + "".join(
        f'<div class="card"><a href="{fn.replace(".md", ".html")}"><b>{esc(label)}</b></a>'
        f'<div class="sub">{esc(desc)}</div></div>'
        for fn, label, desc in DOCS
    )
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(shell("Guidebook", idx_body))
    shutil.copy(os.path.join(OUT_DIR, "index.html"), os.path.join(DOCS_DIR, "index.html"))
    print("Built: index.html (out/ + docs/)")


if __name__ == "__main__":
    main()
