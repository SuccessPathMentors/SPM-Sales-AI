"""Build the visitor-facing widget (public/chat-tree/index.html) and the embed test page from the same template as the review prototype.
Usage: python3 -I build_widget.py tree.json prototype_template.html out_dir
"""
import json, sys, os, re
tree = json.load(open(sys.argv[1], encoding="utf-8"))
tpl = open(sys.argv[2], encoding="utf-8").read()
out = sys.argv[3]
os.makedirs(out, exist_ok=True)

def sub(s, old, new, count=1):
    assert s.count(old) >= 1, "pattern not found: " + old[:60]
    return s.replace(old, new, count)

# 1. head: drop Artifact-only meta, set title
tpl = re.sub(r"<title>.*?</title>\n", "<title>Success Path Mentors</title>\n<meta name=\"robots\" content=\"noindex,nofollow\">\n", tpl, count=1)
tpl = sub(tpl, '<meta name="claude:viewport-fit-sides" content="cover">\n', "")

# 2. markup: replace the review desk with a widget-only layout
start = tpl.index('<div class="wrap">')
end = tpl.index('<script type="application/json" id="tree-data">')
widget = '''<div class="widget" id="app">
  <div class="w-head">
    <span class="brand">Success Path Mentors</span>
    <div class="seg" role="group" aria-label="Language">
      <button type="button" data-lang="ar" aria-pressed="true">العربية</button>
      <button type="button" data-lang="en" aria-pressed="false">English</button>
      <button type="button" data-lang="fr" aria-pressed="false">Français</button>
    </div>
    <button type="button" class="tb" id="closeChat" hidden aria-label="Close">✕</button>
  </div>
  <div class="toolbar" id="toolbar"></div>
  <nav class="crumbs" id="crumbs" aria-label="Path"></nav>
  <div class="log" id="log" role="log" aria-live="polite"></div>
  <div class="w-foot"><span id="footnote"></span><button type="button" class="link" id="humanBtn"></button></div>
  <aside class="mapdrawer" id="drawer" hidden aria-label="Map">
    <div class="p-head"><h2 id="mapTitle"></h2><span><button type="button" class="tb" id="toggleAll">+</button> <button type="button" class="tb" id="closeMap" aria-label="Close">✕</button></span></div>
    <ul class="tree" id="tree"></ul>
  </aside>
</div>

'''
tpl = tpl[:start] + widget + tpl[end:]

# 3. CSS overrides appended before </style>
css = '''
/* visitor widget: fill the frame */
[hidden]{display:none!important}
html,body{height:100%}
body{padding:0;margin:0;background:var(--surface)}
.widget{position:relative;height:100vh;height:100dvh;min-height:0;border:0;border-radius:0}
.mapdrawer{position:absolute;inset:0;background:var(--surface);z-index:5;overflow:auto;padding:14px 16px;display:grid;gap:12px;align-content:start}
'''
css += '''
a.btn{display:inline-block;text-decoration:none}
/* site brand blue (matches the website chat colours) */
:root{--accent:#1d5fb8;--accent-soft:#e4eefb;--bg:#f3f7fc;--line:#d7e2f0}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--accent:#8ec0f7;--accent-ink:#0b1f3a;--accent-soft:#16304f}}
'''
tpl = sub(tpl, "</style>", css + "</style>")

# 4. JS patches
tpl = sub(tpl, "function renderStats(){", "function renderStats(){ if(!$(\"stats\"))return;")
tpl = sub(tpl, "  mk(ICON.fwd,UI.fwd[l],forward,!S.fwd.length);\n",
          "  mk(ICON.fwd,UI.fwd[l],forward,!S.fwd.length);\n  mk(ICON.map,UI.map[l],function(){$(\"drawer\").hidden=!$(\"drawer\").hidden});\n")
tpl = sub(tpl, " fwd:'<svg", " map:'<svg viewBox=\"0 0 16 16\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M2 4h12M2 8h8M2 12h5\"/></svg>',\n fwd:'<svg")
tpl = sub(tpl, "nb.addEventListener(\"click\",function(){ if(ok)jump(id); });", "nb.addEventListener(\"click\",function(){ if(ok){jump(id);$(\"drawer\").hidden=true} });")
tpl = sub(tpl, 'if(n.origin==="composed")row.appendChild', 'if(REVIEW && n.origin==="composed")row.appendChild')
tpl = sub(tpl, 'if(!ok)row.appendChild(el("span","tag dim","غير متاح"));', 'if(REVIEW && !ok)row.appendChild(el("span","tag dim","غير متاح"));')
tpl = sub(tpl, 'row.appendChild(el("span","mono",id));', 'if(REVIEW)row.appendChild(el("span","mono",id));')
tpl = sub(tpl, 'var S = {', 'var REVIEW = !/[?&]clean=1/.test(location.search);\nvar REGURL = null;\ntry { var qr = /[?&]reg=([^&]+)/.exec(location.search); if (qr) { var ru = decodeURIComponent(qr[1]); if (/^\\/[A-Za-z0-9_\\-\\/]*$/.test(ru) && ru.indexOf("//") !== 0) REGURL = ru; } } catch (e) {}\nvar S = {')
tpl = sub(tpl, '$("footnote").textContent=W.note[l];', '$("footnote").textContent=REVIEW?W.note[l]:"";\n  $("mapTitle").textContent=UI.map[l]; $("drawer").dir=dirOf(l);')
tpl = sub(tpl, "renderStats(); render(false);",
          '$("closeMap").addEventListener("click",function(){$("drawer").hidden=true});\n'
          'document.addEventListener("keydown",function(e){if(e.key==="Escape")$("drawer").hidden=true});\n'
          'if(/[?&]close=1/.test(location.search)){ $("closeChat").hidden=false; $("closeChat").addEventListener("click",function(){ try{ window.parent.postMessage({type:"spm-guided-chat-close"}, location.origin) }catch(e){} }); }\n'
          'var qm=/[?&]lang=(ar|en|fr)/.exec(location.search); if(qm){S.lang=qm[1]; document.documentElement.lang=qm[1]}\n'
          'renderStats(); render(false);')

tpl = sub(tpl, ' note:{ar:"نموذج تجريبي"', ' liveReg:{ar:"للتسجيل، تابعوا إلى صفحة التسجيل الآمنة في موقعنا.",en:"To register, continue to the registration page on our website.",fr:"Pour vous inscrire, continuez vers la page d’inscription de notre site."},\n go:{ar:"الانتقال إلى التسجيل",en:"Go to registration",fr:"Aller à l’inscription"},\n note:{ar:"نموذج تجريبي"')
tpl = sub(tpl, 'function renderWizard(box){\n  var r=S.reg, l=S.lang, d=r.data;',
  'function renderWizard(box){\n  var r=S.reg, l=S.lang, d=r.data;\n  if(REGURL){ box.appendChild(el("strong",null,W.liveReg[l])); var ra=document.createElement("a"); ra.className="btn"; ra.href=REGURL; ra.target="_top"; ra.textContent=W.go[l]; var rr=el("div","row"); rr.appendChild(ra); box.appendChild(rr); return; }')
tpl = sub(tpl, 'bot.appendChild(el("div",null,L(n.text)||"")); var box=el("div");', 'bot.appendChild(el("div",null,REGURL?"":(L(n.text)||""))); var box=el("div");')

j = json.dumps(tree, ensure_ascii=False).replace("</", "<\\/")
html = "<!doctype html>\n<html lang=\"ar\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n" + tpl.replace("/*TREE_JSON*/", j) + "\n</html>\n"
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)

test = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Guided chat test</title>
<style>
body{margin:0;font-family:system-ui,Arial,sans-serif;background:#f4f7f7;color:#14262b;padding:24px}
p{max-width:60ch;line-height:1.6}
#spm-launch{position:fixed;right:20px;bottom:20px;border:0;border-radius:999px;background:#0f6b5c;color:#fff;padding:14px 20px;font:600 15px system-ui;cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,.25)}
#spm-frame{position:fixed;right:20px;bottom:80px;width:400px;height:680px;max-height:calc(100vh - 100px);border:1px solid #d2dbde;border-radius:14px;box-shadow:0 10px 40px rgba(0,0,0,.3);background:#fff;overflow:hidden}
#spm-frame[hidden]{display:none}
#spm-frame iframe{width:100%;height:100%;border:0}
@media (max-width:520px){#spm-frame{inset:0;width:auto;height:auto;max-height:none;border-radius:0;right:0;bottom:0}}
</style></head><body>
<h1>Guided chat — test page</h1>
<p>Not linked from the site and not indexed. This page shows how the guided chat sits on a website page. The live chatbot is untouched. Registration here is a simulation and sends nothing.</p>
<button id="spm-launch" type="button">Chat</button>
<div id="spm-frame" hidden><iframe title="Success Path Mentors chat" src="/chat-tree/index.html"></iframe></div>
<script>
var b=document.getElementById("spm-launch"),f=document.getElementById("spm-frame");
b.addEventListener("click",function(){f.hidden=!f.hidden});
</script></body></html>
'''
open(os.path.join(out, "test.html"), "w", encoding="utf-8").write(test)
print("ok", os.path.getsize(os.path.join(out, "index.html")))
