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
     "Survey results, theories and linked recommendations."),
    ("DOC3-mix-textbook.md", "Mix Textbook — Teacher Lessons",
     "15-minute lesson scripts, activities and class norms."),
]

# Teacher collection: paste your Google Apps Script Web App URL here, rebuild + push.
# Empty = Send button shows setup hint. Example: "https://script.google.com/macros/s/ABC.../exec"
TEACHER_ENDPOINT = "https://script.google.com/macros/s/AKfycbyK66DvH--P53Ok_f_9WuCFQZ2MShrf2JyuH4Km0j-QELoOc0lezz_Pods8EvZKBRzB/exec"


def esc(s):
    return html.escape(s or "", quote=True)


REVEAL_JS = """var o=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add("on");o.unobserve(en.target)}})},{threshold:.08});"""


def shell(title, body_inner):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="Study guide: routines, evidence and lessons for effective online learning.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@600;800&display=swap" rel="stylesheet">
<style>
body{{background:radial-gradient(circle at top right,#0f172a,#020617);background-color:#020617;color:#f1f5f9;font-family:'Inter',ui-sans-serif,system-ui,sans-serif;margin:0;line-height:1.65;counter-reset:fig}}
body::before{{content:"";position:fixed;inset:0;background-image:radial-gradient(rgba(129,140,248,.13) 1px,transparent 1px);background-size:26px 26px;pointer-events:none}}
h1,h2,h3{{font-family:'Outfit','Inter',sans-serif}}
p{{margin:10px 0}}
.wrap{{max-width:960px;margin:0 auto;padding:24px 16px 64px;position:relative}}
.topbar{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
.topbar a{{color:#94a3b8;text-decoration:none;font-size:14px}}
.eyebrow{{color:#818cf8;font-weight:600;letter-spacing:.18em;text-transform:uppercase;font-size:12px}}
.grad{{background:linear-gradient(135deg,#818cf8,#c084fc);-webkit-background-clip:text;background-clip:text;color:transparent}}
.card,.glass{{background:rgba(255,255,255,.04);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.1);border-radius:20px;padding:20px;margin:14px 0;transition:transform .2s ease-out,border-color .2s}}
.card:hover{{transform:translateY(-3px);border-color:rgba(129,140,248,.5)}}
.tldr{{background:rgba(129,140,248,.08);border:1px solid rgba(129,140,248,.3);border-left:4px solid #818cf8;border-radius:14px;padding:16px;margin:14px 0}}
.badge{{display:inline-block;background:rgba(129,140,248,.15);color:#c7d2fe;border-radius:999px;padding:2px 10px;font-size:12px;margin-right:6px}}
.muted{{color:#94a3b8;font-size:13px}}
.sec{{margin-top:28px}}
h1{{font-size:26px;margin:8px 0}}h2{{font-size:19px;margin:0 0 8px}}h3{{font-size:16px;margin:14px 0 6px}}
.grid2{{display:grid;grid-template-columns:1fr;gap:14px}}
@media(min-width:720px){{.grid2{{grid-template-columns:1fr 1fr}}}}
a{{color:#a5b4fc}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid rgba(255,255,255,.1);vertical-align:top}}
th{{color:#c7d2fe;font-weight:600}}
.placeholder{{border:1.5px dashed #64748b;border-radius:14px;padding:14px 16px;margin:12px 0;background:rgba(255,255,255,.03);color:#94a3b8;font-size:14px;list-style:none}}
.pic{{margin:14px auto;text-align:center;max-width:480px}}
.pic svg{{max-width:100%;height:auto;background:linear-gradient(180deg,#ffffff,#eef2ff);border:1px solid rgba(255,255,255,.15);border-radius:16px;box-shadow:0 8px 30px rgba(0,0,0,.45);counter-increment:fig}}
.pic figcaption,.pic .cap{{color:#94a3b8;font-size:13px;margin-top:8px}}
.pic figcaption::before{{content:"Figure " counter(fig) " — "}}
li.pic{{list-style:none}}
.toc{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px}}
@media(min-width:720px){{.toc{{position:sticky;top:0;z-index:5;background:rgba(2,6,23,.85);backdrop-filter:blur(12px);padding:10px 0}}.toc.scrolled{{box-shadow:0 8px 24px rgba(0,0,0,.4)}}}}
.toc a{{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:999px;padding:5px 14px;font-size:13px;color:#e2e8f0;text-decoration:none;transition:all .15s}}
.toc a:hover{{border-color:rgba(129,140,248,.6);transform:translateY(-2px)}}
.toc a.s{{font-size:12px;color:#94a3b8;padding:3px 10px}}
.dbody{{display:grid;grid-template-rows:0fr;transition:grid-template-rows .28s ease-out}}
details[open]>.dbody{{grid-template-rows:1fr}}
.dbody-in{{overflow:hidden;min-height:0}}
.hero{{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px 20px}}
.hero h1,.hero h3,.hero p,.hero .sub{{width:100%;max-width:70ch;margin-left:auto!important;margin-right:auto!important;text-align:center!important}}
.hero h1{{font-size:clamp(30px,5vw,46px);margin:10px auto;background:linear-gradient(135deg,#a5b4fc,#e9d5ff);-webkit-background-clip:text;background-clip:text;color:transparent}}
.hero .sub{{font-size:16px}}
.chapter{{border-top:3px solid #818cf8}}
details.chapter:nth-of-type(4n+1){{border-top-color:#818cf8}}
details.chapter:nth-of-type(4n+2){{border-top-color:#34d399}}
details.chapter:nth-of-type(4n+3){{border-top-color:#fbbf24}}
details.chapter:nth-of-type(4n){{border-top-color:#fb7185}}
.chapter p,.chapter li{{max-width:70ch}}
.chapter h2{{margin-top:14px}}
.chapter h3{{color:#c7d2fe}}
.chapter h3.warn{{color:#fda4af}}
details.chapter summary{{cursor:pointer;list-style:none}}
details.chapter summary::-webkit-details-marker{{display:none}}
details.chapter summary h2{{display:inline}}
details.chapter summary::after{{content:"+";float:right;color:#818cf8;font-weight:800;font-size:20px}}
details.chapter[open] summary::after{{content:"–"}}
.dbody{{display:grid;grid-template-rows:0fr;transition:grid-template-rows .28s ease-out}}
details[open]>.dbody{{grid-template-rows:1fr}}
.dbody-in{{overflow:hidden}}
.steps{{display:grid;grid-template-columns:1fr;gap:10px;margin:12px 0}}
@media(min-width:720px){{.steps{{grid-template-columns:repeat(4,1fr)}}}}
.step{{background:rgba(129,140,248,.08);border:1px solid rgba(129,140,248,.3);border-radius:14px;padding:12px;text-align:center;font-size:14px}}
.step .n{{display:flex;width:26px;height:26px;border-radius:50%;background:#818cf8;color:#020617;align-items:center;justify-content:center;margin:0 auto 6px;font-size:14px;flex:none}}
.check{{display:flex;gap:10px;align-items:flex-start;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.08);cursor:pointer}}
.check:last-child{{border-bottom:none}}
.check input{{width:19px;height:19px;margin-top:2px;accent-color:#818cf8;flex:none}}
.planner{{display:grid;grid-template-columns:1.4fr repeat(7,30px);gap:6px;align-items:center;margin:10px 0;font-size:13px}}
.planner .dh{{text-align:center;color:#94a3b8;font-size:11px}}
.planner button.dot{{width:26px;height:26px;border-radius:50%;border:1px solid rgba(255,255,255,.25);background:transparent;cursor:pointer;padding:0;transition:all .15s}}
.planner button.dot:hover{{border-color:#818cf8;transform:scale(1.12)}}
.planner button.dot.on{{background:linear-gradient(135deg,#818cf8,#c084fc);border-color:transparent}}
.planner button.dot.off{{opacity:.22;pointer-events:none}}
.planner .dh.on{{color:#e0e7ff;font-weight:800}}
.checkrow{{border-bottom:1px solid rgba(255,255,255,.08)}}
.checkrow:last-child{{border-bottom:none}}
.howbtn{{margin-left:auto;flex:none;background:rgba(129,140,248,.12);border:1px solid rgba(129,140,248,.4);color:#c7d2fe;border-radius:999px;padding:2px 10px;font-size:12px;cursor:pointer}}
.howbtn:hover{{border-color:#818cf8}}
.howpanel{{background:rgba(129,140,248,.07);border:1px solid rgba(129,140,248,.25);border-radius:12px;padding:10px 12px;margin:0 0 10px;font-size:13px}}
.howpanel b.t{{color:#e0e7ff}}
.howpanel ul{{margin:6px 0 6px 18px;padding:0}}
.howpanel .ok{{color:#6ee7b7;font-size:13px;margin-top:6px}}
.howpanel .bad{{color:#fda4af;font-size:13px;margin-top:6px}}
.note{{width:100%;box-sizing:border-box;background:rgba(2,6,23,.6);border:1px solid rgba(255,255,255,.2);color:#f1f5f9;border-radius:10px;padding:8px;font-size:13px;margin-top:6px}}
.mini{{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.15);color:#e2e8f0;border-radius:999px;padding:4px 12px;font-size:12px;cursor:pointer;margin:6px 6px 0 0}}
.mini:hover{{border-color:#818cf8}}
.daypick{{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}}
.daypick button{{background:transparent;border:1px solid rgba(255,255,255,.25);color:#cbd5e1;border-radius:999px;padding:4px 12px;font-size:12px;cursor:pointer}}
.daypick button.on{{background:linear-gradient(135deg,#818cf8,#c084fc);color:#020617;border-color:transparent;font-weight:800}}
.daypick button.q{{border-style:dashed;color:#94a3b8}}
.prof{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0;font-size:13px}}
.prof input{{background:rgba(2,6,23,.6);border:1px solid rgba(255,255,255,.2);color:#f1f5f9;border-radius:10px;padding:6px 10px;font-size:13px;min-width:140px}}
.expout{{width:100%;box-sizing:border-box;background:rgba(2,6,23,.6);border:1px solid rgba(255,255,255,.2);color:#cbd5e1;border-radius:10px;padding:8px;font-size:12px;margin-top:8px;white-space:pre-wrap}}
.progress{{background:linear-gradient(135deg,rgba(129,140,248,.25),rgba(192,132,252,.18));border:1px solid rgba(129,140,248,.4);border-radius:14px;padding:12px 16px;margin:12px 0;font-size:14px}}
.rv{{opacity:0;transform:translateY(14px);transition:opacity .5s ease-out,transform .5s ease-out}}
.rv.on{{opacity:1;transform:none}}
.bar{{transform:scaleX(0);transform-box:fill-box;transform-origin:left;animation:grow .7s ease-out forwards}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
a:focus-visible,button:focus-visible,summary:focus-visible,input:focus-visible{{outline:2px solid #818cf8;outline-offset:2px}}
@media(min-width:1100px){{.wrap{{max-width:1100px}}.grid2{{grid-template-columns:1fr 1fr 1fr}}}}
@media print{{body{{background:#fff;color:#111}}body::before{{display:none}}.hero h1{{color:#111!important;background:none!important;-webkit-text-fill-color:#111!important}}.topbar,.toc,.progress{{display:none}}.wrap{{max-width:100%;padding:0}}.card,.tldr,.chapter,figure{{background:#fff!important;color:#111!important;border:1px solid #ccc!important;box-shadow:none!important;backdrop-filter:none!important}}.tldr{{border-left:4px solid #111!important}}.muted,.cap,.pic figcaption,.sub{{color:#444!important}}a{{color:#111}}.rv{{opacity:1!important;transform:none!important}}.bar{{animation:none;transform:none}}.grad{{color:#111;-webkit-text-fill-color:#111}}.chapter{{break-inside:avoid}}}}
@media (prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important}}.rv{{opacity:1;transform:none}}.bar{{transform:none}}}}
</style>
</head>
<body>
<div class="wrap mx-auto px-4">
<div class="topbar"><a href="index.html">&larr; Alph</a><span class="muted">Guidebook</span></div>
{body_inner}
</div>
<script>
(function(){{
var UKEY="gb-user-v3";
var TEACHER_URL="{TEACHER_ENDPOINT}";
var user="";try{{user=(localStorage.getItem(UKEY)||"").trim()}}catch(e){{}}
function kk(base){{return base+(user?"-"+user:"")}}
function loadJ(k,fb){{try{{var v=localStorage.getItem(k);if(v===null)return fb;return JSON.parse(v)}}catch(e){{return fb}}}}
function hasK(k){{try{{return localStorage.getItem(k)!==null}}catch(e){{return false}}}}
var R=loadJ(kk("gb-routines-v3"),{{}}),W=loadJ(kk("gb-week-v3"),{{}}),N=loadJ(kk("gb-notes-v3"),{{}});
var D;if(hasK(kk("gb-days-v3"))){{D=loadJ(kk("gb-days-v3"),{{}})}}else{{D={{"0":1,"1":1,"2":1,"3":1,"4":1}}}}
function save(){{try{{localStorage.setItem(kk("gb-routines-v3"),JSON.stringify(R));localStorage.setItem(kk("gb-week-v3"),JSON.stringify(W));localStorage.setItem(kk("gb-notes-v3"),JSON.stringify(N));localStorage.setItem(kk("gb-days-v3"),JSON.stringify(D))}}catch(e){{}}}}
function iso(d){{return d.getFullYear()+"-"+("0"+(d.getMonth()+1)).slice(-2)+"-"+("0"+d.getDate()).slice(-2)}}
function monday(){{var d=new Date();d.setDate(d.getDate()-((d.getDay()+6)%7));return d}}
function wdi(dt){{return (dt.getDay()+6)%7}}
function onDay(di){{return !!D[String(di)] }}
function onlineCount(){{var n=0;for(var i=0;i<7;i++)if(onDay(i))n++;return n}}
function dayCount(key){{var b=W[key]||{{}};return Object.keys(b).length}}
function weekMarks(){{var m=iso(monday()),n=0;Object.keys(W).forEach(function(k){{if(k<m)return;var dt;try{{dt=new Date(k+"T12:00:00")}}catch(e){{return}};if(!onDay(wdi(dt)))return;n+=Object.keys(W[k]).length}});return n}}
function streak(){{var d=new Date(),s=0,g=0;var td=wdi(d);if(!onDay(td)||dayCount(iso(d))<2){{d.setDate(d.getDate()-1);g++}}while(g<40){{var di=wdi(d);if(!onDay(di)){{d.setDate(d.getDate()-1);g++;continue}}if(dayCount(iso(d))>=2){{s++;d.setDate(d.getDate()-1);g++}}else break}}return s}}
function summary(){{var boxes=document.querySelectorAll("[data-check]");var done=0;boxes.forEach(function(el){{if(R[el.getAttribute("data-check")])done++}});var days=[];for(var i=0;i<7;i++)if(onDay(i))days.push(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][i]);var notes=[];document.querySelectorAll("[data-note]").forEach(function(el){{var v=(N[el.getAttribute("data-note")]||"").trim();if(v)notes.push("- "+v.slice(0,140))}});return "Guidebook progress"+(user?" ("+user+")":"")+" "+iso(new Date())+"\\nRoutines: "+done+"/"+boxes.length+"\\nWeek: "+weekMarks()+"/"+(onlineCount()*4)+" (online: "+(days.join(",")||"none")+")\\nStreak: "+streak()+"d"+(notes.length?"\\nMy texts:\\n"+notes.join("\\n"):"")}}
function paint(){{
 var boxes=document.querySelectorAll("[data-check]");
 boxes.forEach(function(el){{el.checked=!!R[el.getAttribute("data-check")]}});
 document.querySelectorAll("[data-self]").forEach(function(el){{el.checked=!!R[el.getAttribute("data-self")]}});
 document.querySelectorAll("[data-note]").forEach(function(el){{var k=el.getAttribute("data-note");if(document.activeElement!==el&&N[k]!==undefined)el.value=N[k]}});
 document.querySelectorAll("[data-user]").forEach(function(el){{if(document.activeElement!==el)el.value=user}});
 document.querySelectorAll("[data-day]").forEach(function(el){{var on=onDay(el.getAttribute("data-day"));if(on)el.classList.add("on");else el.classList.remove("on")}});
 document.querySelectorAll("[data-dh]").forEach(function(el){{var on=onDay(el.getAttribute("data-dh"));if(on)el.classList.add("on");else el.classList.remove("on")}});
 var done=0;boxes.forEach(function(el){{if(R[el.getAttribute("data-check")])done++}});
 var mon=monday();
 document.querySelectorAll("[data-w]").forEach(function(el){{
  var parts=el.getAttribute("data-w").split("|");var di=parseInt(parts[1],10);
  var dt=new Date(mon);dt.setDate(mon.getDate()+di);
  var day=W[iso(dt)]||{{}},on=!!day[parts[0]];
  el.classList.toggle("on",!!on);
  el.classList.toggle("off",!onDay(di));
  el.disabled=!onDay(di);
  el.title=!onDay(di)?"Not an online day - pick it above to enable":"";
  el.setAttribute("aria-pressed",on?"true":"false");
 }});
 var p=document.getElementById("progress");
 if(p){{var yc=onlineCount()*4;var msg="<b>My progress"+(user?" ("+user.replace(/</g,"&lt;")+")":"")+"</b> - routines "+done+"/"+boxes.length+" &middot; week "+weekMarks()+"/"+yc+" &middot; streak "+streak()+"d";if(!onlineCount())msg+=" - pick your online days above";p.innerHTML=msg}}
}}
document.addEventListener("change",function(e){{
 var el=e.target;
 if(el.hasAttribute&&el.hasAttribute("data-check")){{var k=el.getAttribute("data-check");if(el.checked){{R[k]=1;var hp=document.querySelector('[data-howpanel="'+k+'"]');if(hp)hp.hidden=false}}else delete R[k];save();paint()}}
 else if(el.hasAttribute&&el.hasAttribute("data-self")){{var k2=el.getAttribute("data-self");if(el.checked)R[k2]=1;else delete R[k2];save();paint()}}
}});
document.addEventListener("input",function(e){{
 var el=e.target;
 if(el.hasAttribute&&el.hasAttribute("data-note")){{N[el.getAttribute("data-note")]=el.value;try{{localStorage.setItem(kk("gb-notes-v3"),JSON.stringify(N))}}catch(err){{}}}}
 if(el.hasAttribute&&el.hasAttribute("data-user")){{return}}
}});
document.addEventListener("click",function(e){{
 var h=e.target.closest?e.target.closest("[data-how]"):null;
 if(h){{var k=h.getAttribute("data-how");var p=document.querySelector('[data-howpanel="'+k+'"]');if(p)p.hidden=!p.hidden;return}}
 var db=e.target.closest?e.target.closest("[data-day]"):null;
 if(db){{var di=db.getAttribute("data-day");if(D[di])delete D[di];else D[di]=1;save();paint();return}}
 var da=e.target.closest?e.target.closest("[data-dayact]"):null;
 if(da){{var a=da.getAttribute("data-dayact");if(a==="all")D={{"0":1,"1":1,"2":1,"3":1,"4":1,"5":1,"6":1}};else if(a==="weekdays")D={{"0":1,"1":1,"2":1,"3":1,"4":1}};else D={{}};save();paint();return}}
 var gc=e.target.closest?e.target.closest("[data-goalcheck]"):null;
 if(gc){{var k3=gc.getAttribute("data-goalcheck");var ta=document.querySelector('[data-note="'+k3+'-note"]');var msg=document.querySelector('[data-goalmsg="'+k3+'"]');var v=ta&&ta.value?ta.value.trim():"";var hasNum=/\d/.test(v);var hasTime=/(before|by|tomorrow|tonight|today|pm|am|min|week|mon|tue|wed|thu|fri)/i.test(v);var pts=(v.length>=12?1:0)+(hasNum?1:0)+(hasTime?1:0);if(msg){{msg.hidden=false;if(pts>=2){{msg.className="ok";msg.textContent="Looks good ("+pts+"/3): has detail + number/time. Now tick Done."}}else{{msg.className="bad";msg.textContent="Add more ("+pts+"/3): need 12+ chars"+(hasNum?"":" + a number")+(hasTime?"":" + a time/deadline")+". See example above."}}}}return}}
 var ex=e.target.closest?e.target.closest("[data-exp]"):null;
 if(ex){{var k4=ex.getAttribute("data-exp");var out=document.querySelector("[data-expout]");
  if(k4==="saveuser"){{var inp=document.querySelector("[data-user]");user=inp&&inp.value?inp.value.trim():"";try{{localStorage.setItem(UKEY,user)}}catch(err){{}}R=loadJ(kk("gb-routines-v3"),{{}});W=loadJ(kk("gb-week-v3"),{{}});N=loadJ(kk("gb-notes-v3"),{{}});if(hasK(kk("gb-days-v3")))D=loadJ(kk("gb-days-v3"),{{}});else D={{"0":1,"1":1,"2":1,"3":1,"4":1}};save();paint();return}}
  if(k4==="download"){{var s2=summary();try{{var b=new Blob([s2],{{type:"text/plain"}});var a2=document.createElement("a");a2.href=URL.createObjectURL(b);a2.download="guidebook-progress"+(user?"-"+user:"")+".txt";a2.click();setTimeout(function(){{URL.revokeObjectURL(a2.href)}},2000)}}catch(err){{}}return}}
  if(k4==="send"){{if(!TEACHER_URL){{if(out){{out.hidden=false;out.textContent="Teacher link not set yet. Tap Download to save your progress for now."}}return}}var payload={{user:user||"(no code)",summary:summary(),routines:R,week:W,notes:N,days:D,at:new Date().toISOString()}};if(out){{out.hidden=false;out.textContent="Sending..."}}try{{fetch(TEACHER_URL,{{method:"POST",mode:"no-cors",headers:{{"Content-Type":"text/plain"}},body:JSON.stringify(payload)}}).then(function(){{if(out)out.textContent="Sent. Thank you."}},function(){{if(out)out.textContent="Sent (if offline, use Download instead)."}})}}catch(err){{if(out)out.textContent="Send failed. Use Download instead."}}return}}
  if(k4==="reset"){{if(confirm("Reset progress on this device"+(user?" for "+user:"")+"?")){{R={{}};W={{}};N={{}};save();paint()}}return}}
 }}
 var w=e.target.closest?e.target.closest("[data-w]"):null;
 if(w){{if(w.disabled)return;var parts=w.getAttribute("data-w").split("|");var mon=monday(),dt=new Date(mon);dt.setDate(mon.getDate()+parseInt(parts[1],10));var key=iso(dt);W[key]=W[key]||{{}};if(W[key][parts[0]])delete W[key][parts[0]];else W[key][parts[0]]=1;save();paint();return}}
 var t=e.target.closest?e.target.closest(".toc a"):null;
 if(t){{var id=t.getAttribute("href");
  if(id&&id.charAt(0)==="#"){{var d=document.getElementById(id.slice(1));
   if(d){{var det=d.closest("details");if(det)det.open=true}}}}
 }}
}});
function openHash(){{
 var id=location.hash;
 if(id&&id.length>1){{var d=document.getElementById(id.slice(1));
  if(d){{var det=d.closest?d.closest("details"):null;
   if(det){{det.open=true;det.scrollIntoView()}}}}
 }}
}}
var snapshot=[];
window.addEventListener("beforeprint",function(){{
 snapshot=[];
 document.querySelectorAll("details.chapter").forEach(function(d){{snapshot.push(d.open);d.open=true}});
}});
window.addEventListener("afterprint",function(){{
 document.querySelectorAll("details.chapter").forEach(function(d,i){{d.open=!!snapshot[i]}});
}});
window.addEventListener("hashchange",openHash);
function reveal(){{
 var els=document.querySelectorAll("details.chapter,.card,figure.pic");
 els.forEach(function(el){{el.classList.add("rv")}});
 if(!("IntersectionObserver" in window)){{els.forEach(function(el){{el.classList.add("on")}});return}}
 /*__REVEAL__*/
 els.forEach(function(el){{o.observe(el)}});
}}
function shadow(){{
 var t=document.querySelector(".toc");if(!t)return;
 t.classList.toggle("scrolled",window.scrollY>4);
}}
window.addEventListener("scroll",shadow,{{passive:true}});
reveal();shadow();openHash();
paint();
}})();
</script>
</body>
</html>""".replace("/*__REVEAL__*/", REVEAL_JS)


def inline(s):
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", s)
    return s


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


SVG_TIMER = """<svg viewBox="0 0 600 210" role="img" aria-label="Three steps: set timer, focus one tab, tick checklist"><rect x="8" y="8" width="187" height="194" rx="14" fill="#fff" stroke="#1a1a1a" stroke-width="3"/><circle cx="34" cy="34" r="14" fill="#818cf8"/><text x="34" y="39" text-anchor="middle" font-size="14" font-weight="bold" fill="#fff">1</text><circle cx="101" cy="100" r="36" fill="#fff" stroke="#1a1a1a" stroke-width="4"/><circle cx="101" cy="100" r="5" fill="#1a1a1a"/><line x1="101" y1="100" x2="101" y2="72" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/><line x1="101" y1="100" x2="122" y2="110" stroke="#0f62fe" stroke-width="4" stroke-linecap="round"/><text x="101" y="176" text-anchor="middle" font-size="14" font-weight="bold" fill="#1a1a1a">Set 25-5</text><rect x="203" y="8" width="187" height="194" rx="14" fill="#fff" stroke="#1a1a1a" stroke-width="3"/><circle cx="229" cy="34" r="14" fill="#818cf8"/><text x="229" y="39" text-anchor="middle" font-size="14" font-weight="bold" fill="#fff">2</text><rect x="243" y="66" width="110" height="66" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="3"/><rect x="243" y="66" width="110" height="20" rx="8" fill="#e7e5e4"/><rect x="249" y="70" width="42" height="12" rx="4" fill="#0f62fe"/><line x1="253" y1="104" x2="343" y2="104" stroke="#e7e5e4" stroke-width="5" stroke-linecap="round"/><line x1="253" y1="118" x2="315" y2="118" stroke="#e7e5e4" stroke-width="5" stroke-linecap="round"/><text x="296" y="176" text-anchor="middle" font-size="14" font-weight="bold" fill="#1a1a1a">One tab</text><rect x="398" y="8" width="187" height="194" rx="14" fill="#fff" stroke="#1a1a1a" stroke-width="3"/><circle cx="424" cy="34" r="14" fill="#818cf8"/><text x="424" y="39" text-anchor="middle" font-size="14" font-weight="bold" fill="#fff">3</text><rect x="433" y="72" width="17" height="17" rx="4" fill="none" stroke="#1a1a1a" stroke-width="2"/><polyline points="435,80 440,85 448,75" fill="none" stroke="#0f62fe" stroke-width="3"/><line x1="458" y1="80" x2="545" y2="80" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/><rect x="433" y="100" width="17" height="17" rx="4" fill="none" stroke="#1a1a1a" stroke-width="2"/><polyline points="435,108 440,113 448,103" fill="none" stroke="#0f62fe" stroke-width="3"/><line x1="458" y1="108" x2="520" y2="108" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/><text x="491" y="176" text-anchor="middle" font-size="14" font-weight="bold" fill="#1a1a1a">Tick it</text></svg>"""

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


def hbars(title, rows):
    """Horizontal SVG bar chart. rows: [(label, value)]. Sample (n=40) stated in Methods."""
    top, bh, gap = 46, 22, 12
    H = top + len(rows) * (bh + gap) + 14
    maxv = max((v for _, v in rows), default=1) or 1
    p = [f'<svg viewBox="0 0 400 {H}" role="img" aria-label="{esc(title)}">',
         f'<text x="8" y="22" font-size="14" font-weight="bold" fill="#1a1a1a">{esc(title)}</text>']
    y = top
    for lab, v in rows:
        w = 150 * v / maxv
        num = f"{v:.2f}" if isinstance(v, float) else f"{v:d}"
        p.append(f'<text x="8" y="{y + 15}" font-size="12" fill="#1a1a1a">{esc(lab)}</text>')
        p.append(f'<rect x="150" y="{y}" width="150" height="{bh}" rx="5" fill="#e7e5e4"/>')
        p.append(f'<rect class="bar" x="150" y="{y}" width="{w:.0f}" height="{bh}" rx="5" fill="#0f62fe"><title>{esc(lab)}: {num}</title></rect>')
        p.append(f'<text x="{165 + w:.0f}" y="{y + 15}" font-size="12" fill="#57534e">{num}</text>')
        y += bh + gap
    p.append("</svg>")
    return "".join(p)


# Real Week-1 survey aggregates (n=40). % agree = score 4–5/5.
BARRIERS = [("Screen / Zoom fatigue", 55), ("Distracted by apps", 53),
            ("Self-discipline", 40), ("Asking harder", 25)]

GRAPH_CHARTS = [  # most-specific keys first: first match wins
    (("discipline difficulty",), ("Self-discipline difficulty", [("Score 4-5", 40)])),
    (("distraction level",), ("Distraction by apps", [("Score 4-5", 53)])),
    (("asking difficulty",), ("Asking harder online", [("Score 4-5", 25)])),
    (("fatigue level",), ("Screen / Zoom fatigue", [("Score 4-5", 55)])),
    (("barriers by agree",), ("Barriers by agree % (4-5/5)", BARRIERS)),
    (("graph 1", "sessions per week", "current use"), ("Current use", [("Still online", 70), ("2-4 sessions/week", 43), ("Course-dependent", 40), ("6+ / week", 8), ("4-6 / week", 5), ("1 / week", 5)])),
    (("graph 2", "barrier ranking"), ("Barrier ranking (agree %)", BARRIERS)),
    (("graph 3", "perceived benefits", "likert averages"), ("Benefits (Likert avg, 1-5)", [("Remember all content", 3.5), ("Prefer online", 3.0)])),
]


def graph_chart(txt):
    """SVG chart HTML or None. Never invents data: unmapped slots stay placeholders."""
    t = txt.lower()
    for keys, (title, rows) in GRAPH_CHARTS:
        if any(k in t for k in keys):
            return hbars(title, rows)
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
            + rows + '</table><div class="muted">Group-coded from open answers.</div></div>')


def md_to_html(text, extras=None, toc_keep=None):
    out, toc, seen, lines, i = [], [], set(), text.split("\n"), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("### "):
            ht = ln[4:].strip()
            if ht.lower().startswith("watch out"):
                out.append(f'<h3 class="warn">{inline(ln[4:])}</h3>')
            else:
                out.append(f"<h3>{inline(ln[4:])}</h3>")
        elif ln.startswith("## "):
            sid = slug(ln[3:]) or "sec"
            base, n = sid, 1
            while sid in seen:
                n += 1
                sid = f"{base}-{n}"
            seen.add(sid)
            title = ln[3:].strip()
            main = bool(re.match(r"^(Chapter|Lesson|0\.)", title))
            toc.append((sid, title, main))
            out.append(f'<h2 id="{sid}">{inline(ln[3:])}</h2>')
        elif ln.startswith("# "):
            out.append(f"<h1>{inline(ln[2:])}</h1>")
        elif ln.strip() == "---":
            i += 1  # dropped: chapter cards give the separation now
            continue
        elif ln.startswith("> "):
            quotes = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quotes.append(lines[i].strip()[2:].strip())
                i += 1
            if quotes and "how to use" in quotes[0].lower():
                steps = []
                for q in quotes[1:]:
                    q = re.sub(r"^\d+\.\s*", "", q)
                    if q:
                        steps.append(q)
                if steps:
                    cells = "".join(
                        f'<div class="step"><span class="n">{n + 1}</span>{inline(s)}</div>'
                        for n, s in enumerate(steps)
                    )
                    out.append(f"<p>{inline(quotes[0])}</p>" + f'<div class="steps">{cells}</div>')
                    continue
            out.append('<div class="tldr">' + "<br>".join(inline(q) for q in quotes) + "</div>")
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
                kind = slot_kind(txt)
                if kind in ("pic", "chart", "table"):
                    if items:
                        ftag = "<ul>" if len(items) <= 3 else "<ul class='card'>"
                        out.append(ftag + "\n".join(items) + "</ul>")
                        items = []
                    if kind == "pic":
                        out.append(f'<figure class="pic">{pic_svg(txt)}<figcaption>{inline(txt)}</figcaption></figure>')
                    elif kind == "chart":
                        out.append(f'<figure class="pic">{graph_chart(txt)}<figcaption>{inline(txt)}</figcaption></figure>')
                    else:
                        out.append(table_chart(txt))
                else:
                    items.append(f"<li>{inline(txt)}</li>")
                i += 1
            if items:
                # short plain lists don't earn a card; figures/tables carry their own
                tag = "<ul>" if len(items) <= 3 else "<ul class='card'>"
                out.append(tag + "\n".join(items) + "</ul>")
            continue
        elif re.match(r"\d+\. ", ln.strip()):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i].strip()):
                txt = re.sub(r"^\d+\.\s*", "", lines[i].strip())
                kind = slot_kind(txt)
                if kind in ("pic", "chart", "table"):
                    if items:
                        ftag = "<ol>" if len(items) <= 3 else "<ol class='card'>"
                        out.append(ftag + "\n".join(items) + "</ol>")
                        items = []
                    if kind == "pic":
                        out.append(f'<figure class="pic">{pic_svg(txt)}<figcaption>{inline(txt)}</figcaption></figure>')
                    elif kind == "chart":
                        out.append(f'<figure class="pic">{graph_chart(txt)}<figcaption>{inline(txt)}</figcaption></figure>')
                    else:
                        out.append(table_chart(txt))
                else:
                    items.append(f"<li>{inline(txt)}</li>")
                i += 1
            if items:
                otag = "<ol>" if len(items) <= 3 else "<ol class='card'>"
                out.append(otag + "\n".join(items) + "</ol>")
            continue
        else:
            txt = ln.strip()
            kind = slot_kind(txt)
            if kind == "pic":
                out.append(f'<figure class="pic">{pic_svg(txt)}<figcaption>{inline(txt)}</figcaption></figure>')
            elif kind == "chart":
                out.append(f'<figure class="pic">{graph_chart(txt)}<figcaption>{inline(txt)}</figcaption></figure>')
            elif kind == "table":
                out.append(table_chart(txt))
            elif kind == "box":
                out.append(f'<div class="placeholder">{inline(txt)}</div>')
            else:
                out.append(f"<p>{inline(txt)}</p>")
        i += 1
    if toc_keep:
        toc = [e for e in toc if any(k in e[0] for k in toc_keep)]
    return md_assemble(out, toc, extras)


def md_assemble(out, toc, extras):
    hero, rest = group_sections(out, extras)
    if toc:
        nav = '<div class="toc">' + "".join(
            f'<a href="#{esc(sid)}" class="{"m" if main else "s"}">{esc(t)}</a>' for sid, t, main in toc
        ) + "</div>"
        return hero + nav + rest
    return hero + rest


def group_sections(blocks, extras=None):
    """Cover blocks -> hero card; each h2 + following blocks -> collapsible chapter."""
    extras = extras or {}
    idx = [n for n, b in enumerate(blocks) if b.startswith("<h2")]
    if not idx:
        return "", "\n".join(blocks)
    hero = ""
    if idx[0] > 0:
        hero = '<div class="hero card">\n' + "\n".join(blocks[:idx[0]]) + "\n</div>\n"
    rest = []
    for k, s in enumerate(idx):
        e = idx[k + 1] if k + 1 < len(idx) else len(blocks)
        m = re.search(r'id="([^"]+)"', blocks[s])
        sid = m.group(1) if m else ""
        extra = extras.get(sid, "")
        o = " open" if k == 0 else ""
        rest.append(f'<details class="chapter"{o}>\n<summary>{blocks[s]}</summary>\n<div class="dbody"><div class="dbody-in">\n'
                    + "\n".join(blocks[s + 1:e]) + "\n" + extra + "\n</div></div>\n</details>")
    return hero, "\n".join(rest)


CHECKLISTS = {
    "chapter-1-self-regulation-time": [
        "Wrote one SMART goal for tonight",
        "Made tomorrow's ALPEN plan",
        "Finished a 25-5 x2 study block",
    ],
    "chapter-2-distraction-concentration": [
        "Phone in drawer during study",
        "Kept to one browser tab",
        "Turned notifications off",
    ],
    "chapter-3-interaction-support": [
        "Used the question template once",
        "Peer-checked with a classmate",
        "Posted in the class channel",
    ],
    "chapter-4-fatigue-technology": [
        "Studied 50 minutes, moved 10",
        "Did 20-20-20 twice today",
        "Ran the pre-check before a meeting",
    ],
}

PLANNER = [
    ("chapter-1-self-regulation-time", "Planned & timed"),
    ("chapter-2-distraction-concentration", "Distraction-free"),
    ("chapter-3-interaction-support", "Asked & shared"),
    ("chapter-4-fatigue-technology", "Rested & reset"),
]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


HOW = {
    "doc1-chapter-1-self-regulation-time-0": {
        "how": ["Pick ONE task for tomorrow.", "Add a number (how many / what score).", "Add a deadline (before X pm)."],
        "ex": "Finish LMS Unit 3 quiz (20 questions) before 9pm tomorrow, score 70%+.",
        "self": ["Has WHAT + HOW MANY?", "Has WHEN + TARGET?"],
        "note": "Write your SMART goal here:",
    },
    "doc1-chapter-1-self-regulation-time-1": {
        "how": ["List tasks.", "Estimate minutes each.", "Add buffer.", "Order hardest first.", "Tick off at night."],
        "ex": "Math 30m + English 25m + buffer 10m.",
        "self": ["Times fit your free hours?", "Order decided?"],
    },
    "doc1-chapter-1-self-regulation-time-2": {
        "how": ["Set 25-min timer, one tab only.", "5-min break away from screen.", "Repeat once, then 15-min break."],
        "ex": "25 study - 5 break - 25 study - 15 break.",
        "self": ["Phone away?", "Timer used?"],
    },
    "doc1-chapter-2-distraction-concentration-0": {
        "how": ["Put phone in a drawer, not face-down.", "Keep it there the whole block."],
        "ex": "Drawer closed + silent for 25 min.",
        "self": ["Out of reach?", "Full block?"],
    },
    "doc1-chapter-2-distraction-concentration-1": {
        "how": ["Close all tabs except the study tab.", "Park other ideas on paper for later."],
        "ex": "Only LMS tab open.",
        "self": ["Only 1 tab?", "Distractions parked?"],
    },
    "doc1-chapter-2-distraction-concentration-2": {
        "how": ["Phone: Do Not Disturb.", "Laptop: mute chat + browser.", "Turn back on after block."],
        "ex": "DND on for 25 min.",
        "self": ["Phone silent?", "Laptop silent?"],
    },
    "doc1-chapter-3-interaction-support-0": {
        "how": ["Fill: I tried ___. I expected ___ but got ___. My question is ___."],
        "ex": "Tried Q5, expected 70% got 40%. Question: which formula?",
        "self": ["Tried + expected + got filled?", "One clear question?"],
        "note": "Draft your question here:",
    },
    "doc1-chapter-3-interaction-support-1": {
        "how": ["Send your filled template to 1 classmate.", "Ask: what would you try next?"],
        "ex": "Sent template, got 1 suggestion.",
        "self": ["Sent to 1 peer?", "Got a reply?"],
    },
    "doc1-chapter-3-interaction-support-2": {
        "how": ["Post template in class channel / forum.", "Include what you already tried."],
        "ex": "Posted with tried / expected / got.",
        "self": ["Posted?", "Tried-part included?"],
    },
    "doc1-chapter-4-fatigue-technology-0": {
        "how": ["Study 50 min.", "Move 10 min (stand, walk, stretch)."],
        "ex": "50 study - 10 walk.",
        "self": ["Moved?", "No marathon over 60?"],
    },
    "doc1-chapter-4-fatigue-technology-1": {
        "how": ["Every 20 min, look ~6m away.", "Hold 20 seconds. Blink + relax shoulders."],
        "ex": "Did it twice today.",
        "self": ["Twice today?", "20 seconds each?"],
    },
    "doc1-chapter-4-fatigue-technology-2": {
        "how": ["Test internet.", "Test mic + camera.", "Join 2 min early."],
        "ex": "Net + mic + cam OK before meeting.",
        "self": ["All 3 tested?", "Joined early?"],
    },
}


def checklist_html(doc, sid, items):
    parts = []
    for n, t in enumerate(items):
        key = f"{doc}-{sid}-{n}"
        h = HOW.get(key, {})
        lis = "".join(f"<li>{inline(x)}</li>" for x in h.get("how", []))
        sboxes = "".join(
            f'<label class="check"><input type="checkbox" data-self="{key}-s{i}"> {inline(q)}</label>'
            for i, q in enumerate(h.get("self", []))
        )
        note = ""
        if h.get("note"):
            note = (f'<div class="muted">{inline(h["note"])}</div>'
                    f'<textarea class="note" rows="2" data-note="{key}-note" '
                    f'placeholder="Type here - saved on this device"></textarea>'
                    f'<div><button type="button" class="mini" data-goalcheck="{key}">Check my text</button></div>'
                    f'<div class="ok" data-goalmsg="{key}" hidden></div>')
        ex = f'<div class="muted">Example: {inline(h.get("ex", ""))}</div>' if h.get("ex") else ""
        panel = (f'<div class="howpanel" data-howpanel="{key}" hidden>'
                 f'<b class="t">How to do it right</b><ul>{lis}</ul>{ex}'
                 f'<b class="t">Check yourself - tick all, then tick Done</b>{sboxes}{note}</div>')
        parts.append(
            f'<div class="checkrow"><div style="display:flex;gap:8px;align-items:center">'
            f'<label class="check" style="flex:1;border:none;padding:9px 0">'
            f'<input type="checkbox" data-check="{key}"> {inline(t)}</label>'
            f'<button type="button" class="howbtn" data-how="{key}">How?</button></div>{panel}</div>')
    return f'<div class="card"><b>Try it this week - tick when done</b><div class="muted">Tap How? to see steps + self-check.</div>{"".join(parts)}</div>'


def planner_html():
    head = '<span></span>' + "".join(f'<span class="dh" data-dh="{di}">{d}</span>' for di, d in enumerate(DAYS))
    rows = [head]
    for sid, label in PLANNER:
        cells = "".join(
            f'<button type="button" class="dot" data-w="doc1-{sid}|{di}" aria-label="{esc(label)} {d}"></button>'
            for di, d in enumerate(DAYS)
        )
        rows.append(f"<span>{esc(label)}</span>{cells}")
    daybtns = "".join(f'<button type="button" data-day="{di}">{d}</button>' for di, d in enumerate(DAYS))
    return ('<div class="card"><b>My study week - tap each day you kept the routine</b>'
            '<div class="prof"><span class="muted">Your Name:</span>'
            '<input data-user placeholder="e.g. Tung">'
            '<button type="button" class="mini" data-exp="saveuser">Save</button></div>'
            '<div class="muted">Type your name once and tap Save. Use the same name every time so your progress and teacher-sheet rows stay together.</div>'
            '<div class="muted">1) Choose your online days - other days turn grey and are skipped in your score.</div>'
            f'<div class="daypick">{daybtns}'
            '<button type="button" class="q" data-dayact="weekdays">Weekdays</button>'
            '<button type="button" class="q" data-dayact="all">All</button>'
            '<button type="button" class="q" data-dayact="clear">Clear</button></div>'
            '<div class="planner">' + "".join(rows) + "</div>"
            '<div><button type="button" class="mini" data-exp="send">Send to teacher</button>'
            '<button type="button" class="mini" data-exp="download">Download</button>'
            '<button type="button" class="mini" data-exp="reset">Reset</button></div>'
            '<div class="muted">Tap Send to teacher when done. Your code + progress go straight to the teacher sheet. Data stays on your device until you send it.</div>'
            '<div class="expout" data-expout hidden></div></div>')


def doc1_extras():
    return {sid: checklist_html("doc1", sid, items) for sid, items in CHECKLISTS.items()}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    for fn, label, _desc in DOCS:
        with open(os.path.join(BASE_DIR, fn), encoding="utf-8") as f:
            extras = doc1_extras() if fn.startswith("DOC1") else None
            keep = ["results", "chapters", "discussion", "appendix"] if fn.startswith("DOC2") else None
            body = md_to_html(f.read(), extras, keep)
            if extras:
                nc = sum(len(v) for v in CHECKLISTS.values())
                body += planner_html()
                body += f'<div class="progress" id="progress"><b>My progress</b> — routines 0/{nc} · week 0/28 · streak 0d</div>'
            html = shell(label, body)
        name = fn.replace(".md", ".html")
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
            f.write(html)
        shutil.copy(os.path.join(OUT_DIR, name), os.path.join(DOCS_DIR, name))
        print(f"Built: {name}")
    roles = [("I'm a student — give me routines", 0), ("I teach — give me lessons", 2),
             ("I want the evidence", 1)]
    idx_body = ('<div class="hero card"><div class="eyebrow">Asia University · Students</div>'
                '<h1 class="grad">Study Smarter Online</h1>'
                '<div class="sub">Pick the version you need — same research, three doors.</div></div>'
                '<div class="grid2">' + "".join(
        f'<div class="card"><b>{role}</b><div class="sub">{esc(DOCS[i][2])}</div>'
        f'<p><a href="{DOCS[i][0].replace(".md", ".html")}">Start →</a></p></div>'
        for role, i in roles
    ) + "</div>")
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(shell("Guidebook", idx_body))
    shutil.copy(os.path.join(OUT_DIR, "index.html"), os.path.join(DOCS_DIR, "index.html"))
    print("Built: index.html (out/ + docs/)")


if __name__ == "__main__":
    main()
