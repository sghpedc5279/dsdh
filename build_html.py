# -*- coding: utf-8 -*-
"""零依赖 Markdown -> 单文件 HTML 转换器（为两本教材生成评审预览版）。"""
import re, os, sys

def log(m):
    with open(r"C:/Users/sghpe/Desktop/BaiduSyncdisk/两本教材/_progress.log", "a", encoding="utf-8") as f:
        f.write(m + "\n")
        f.flush()

FILES = [
    (r"C:/Users/sghpe/Desktop/BaiduSyncdisk/两本教材/数字人文实验_教材编写.md",
     r"C:/Users/sghpe/Desktop/BaiduSyncdisk/两本教材/数字人文实验_教材预览.html"),
    (r"C:/Users/sghpe/Desktop/BaiduSyncdisk/两本教材/档案智能管理_智能书编写.md",
     r"C:/Users/sghpe/Desktop/BaiduSyncdisk/两本教材/档案智能管理_智能书预览.html"),
    (r"C:/Users/sghpe/Desktop/BaiduSyncdisk/两本教材/数据科学与数字人文_教材编写.md",
     r"C:/Users/sghpe/Desktop/BaiduSyncdisk/两本教材/数据科学与数字人文_教材预览.html"),
]

CSS = """
:root{--ink:#1f2328;--sub:#57606a;--line:#e3e6ea;--bg:#ffffff;--soft:#f6f8fa;--accent:#8a1f1f;--accent2:#1f5fa8;}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;color:var(--ink);background:var(--bg);line-height:1.75;font-size:16px}
.wrap{display:flex;max-width:1280px;margin:0 auto}
nav.toc{position:sticky;top:0;align-self:flex-start;width:280px;height:100vh;overflow:auto;padding:28px 18px;border-right:1px solid var(--line);background:var(--soft);font-size:13.5px}
nav.toc h4{margin:0 0 10px;color:var(--accent);font-size:13px;letter-spacing:.05em}
nav.toc a{display:block;color:var(--sub);text-decoration:none;padding:3px 0;border-bottom:1px dashed transparent}
nav.toc a:hover{color:var(--accent2);border-bottom-color:var(--line)}
nav.toc a.lv1{padding-left:0;font-weight:600;color:var(--ink)}
nav.toc a.lv2{padding-left:12px}
nav.toc a.lv3{padding-left:24px;color:#8a929b}
main{flex:1;min-width:0;padding:40px 56px 120px}
header.cover{border-bottom:3px double var(--accent);padding-bottom:22px;margin-bottom:30px}
header.cover h1{font-size:30px;margin:0 0 6px;color:var(--accent)}
header.cover .meta{color:var(--sub);font-size:14px}
h1,h2,h3,h4{line-height:1.35;scroll-margin-top:20px}
h1{font-size:25px;margin:38px 0 14px;color:var(--accent);border-bottom:2px solid var(--accent);padding-bottom:6px}
h2{font-size:21px;margin:34px 0 12px;color:#9a2b2b}
h3{font-size:18px;margin:26px 0 10px;color:#333}
h4{font-size:16px;margin:20px 0 8px}
p{margin:12px 0}
a{color:var(--accent2);text-decoration:none;border-bottom:1px solid #cfe0f2}
a:hover{color:#0b3d6b}
blockquote{margin:16px 0;padding:12px 18px;background:var(--soft);border-left:4px solid var(--accent);border-radius:0 6px 6px 0;color:#37424d}
blockquote p{margin:6px 0}
code{background:var(--soft);padding:2px 6px;border-radius:4px;font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;font-size:13.5px;color:#b3222b}
.codewrap{position:relative;margin:16px 0}
.copybtn{position:absolute;top:8px;right:8px;z-index:2;background:#fff;border:1px solid var(--line);border-radius:5px;font-size:12px;padding:3px 9px;cursor:pointer;color:var(--sub)}
.copybtn:hover{color:var(--accent2);border-color:var(--accent2)}
pre{background:#1e242b;color:#e6edf3;padding:16px 18px;border-radius:8px;overflow:auto;margin:0}
pre code{background:transparent;color:inherit;padding:0;font-size:13px;line-height:1.6;white-space:pre}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:14px}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--soft);color:var(--ink);font-weight:600}
tr:nth-child(even) td{background:#fafbfc}
ul,ol{padding-left:26px;margin:12px 0}
li{margin:5px 0}
hr{border:none;border-top:1px solid var(--line);margin:30px 0}
figure{margin:18px 0;text-align:center}
figure img{max-width:100%;border:1px solid var(--line);border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.08)}
figcaption{font-size:13px;color:var(--sub);margin-top:8px;padding:0 10px}
.note{font-size:13px;color:var(--sub);background:#fff8e6;border-left:4px solid #e0a800;padding:10px 14px;border-radius:0 6px 6px 0;margin:14px 0}
footer{margin-top:60px;padding-top:18px;border-top:1px solid var(--line);color:var(--sub);font-size:13px}
@media(max-width:900px){nav.toc{display:none}main{padding:24px 18px}}
"""

JS = """
<script>
function copyCode(btn){var c=btn.parentElement.querySelector('code');navigator.clipboard.writeText(c.innerText);btn.textContent='已复制';setTimeout(function(){btn.textContent='复制';},1500);}
</script>
"""

def esc_text(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def esc_attr(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def inline(text):
    # protect code spans
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for p in parts:
        if len(p) >= 2 and p.startswith('`') and p.endswith('`'):
            out.append('<code>'+esc_text(p[1:-1])+'</code>')
        else:
            out.append(inline_format(p))
    return ''.join(out)

def inline_format(s):
    s = esc_text(s)
    # images
    s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',
               lambda m: '<figure><img src="%s" alt="%s"><figcaption>%s</figcaption></figure>' % (esc_attr(m.group(2)), esc_attr(m.group(1)), m.group(1)), s)
    # links
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
               lambda m: '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc_attr(m.group(2)), m.group(1)), s)
    # bold
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    # italic
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    return s

def is_special(line):
    return (line.startswith('#') or line.startswith('>') or line.startswith('```') or
            re.match(r'^\s*-\s+', line) or
            re.match(r'^\s*\d+\.\s+', line) or line.strip() in ('---','***',''))

def cells(line):
    line = line.strip()
    if line.startswith('|'): line = line[1:]
    if line.endswith('|'): line = line[:-1]
    return [c.strip() for c in line.split('|')]

_hcount = [0]
def convert(md):
    lines = md.split('\n')
    i = 0
    html = []
    toc = []
    while i < len(lines):
        line = lines[i]
        if line.startswith('```'):
            lang = line[3:].strip()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith('```'):
                buf.append(lines[i]); i += 1
            i += 1
            code = '\n'.join(buf)
            html.append('<div class="codewrap"><button class="copybtn" onclick="copyCode(this)">复制</button><pre><code>%s</code></pre></div>' % esc_text(code))
        elif line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line[level:].strip()
            _hcount[0] += 1
            hid = 's%d' % _hcount[0]
            html.append('<h%d id="%s">%s</h%d>' % (level, hid, inline(text), level))
            if level in (1,2,3):
                toc.append((level, hid, text))
            i += 1
        elif line.startswith('>'):
            buf = []
            while i < len(lines) and lines[i].startswith('>'):
                l = lines[i]
                buf.append(l[2:] if l.startswith('> ') else (l[1:] if l.startswith('>') else l))
                i += 1
            html.append('<blockquote>'+convert('\n'.join(buf))[0]+'</blockquote>')
        elif line.strip().startswith('|') and i+1 < len(lines) and re.match(r'^\s*\|?[\s:|-]+\|?\s*$', lines[i+1]) and '-' in lines[i+1]:
            header = cells(line); i += 2; body = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                body.append(cells(lines[i])); i += 1
            th = ''.join('<th>%s</th>' % inline(c) for c in header)
            rows = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r) for r in body)
            html.append('<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (th, rows))
        elif re.match(r'^\s*-\s+', line):
            buf = []
            while i < len(lines) and re.match(r'^\s*-\s+', lines[i]):
                buf.append(re.sub(r'^\s*-\s+', '', lines[i])); i += 1
            html.append('<ul>'+''.join('<li>%s</li>' % inline(x) for x in buf)+'</ul>')
        elif re.match(r'^\s*\d+\.\s+', line):
            buf = []
            while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                buf.append(re.sub(r'^\s*\d+\.\s+', '', lines[i])); i += 1
            html.append('<ol>'+''.join('<li>%s</li>' % inline(x) for x in buf)+'</ol>')
        elif line.strip() in ('---','***'):
            html.append('<hr>'); i += 1
        elif line.strip() == '':
            i += 1
        else:
            start = i
            buf = []
            while i < len(lines) and lines[i].strip() != '' and not is_special(lines[i]):
                buf.append(lines[i]); i += 1
            if i == start:   # safety: never loop forever
                i += 1
            html.append('<p>%s</p>' % inline(' '.join(buf)))
    return ''.join(html), toc

def build(md_path, html_path):
    _hcount[0] = 0
    md = open(md_path, encoding='utf-8').read()
    body, toc = convert(md)
    # title = first H1
    m = re.search(r'^#\s+(.+)$', md, re.M)
    title = m.group(1).strip() if m else '教材预览'
    # meta = following blockquote
    meta = ''
    mm = re.search(r'^#\s+.*?\n(>.*?)(?:\n\n|\n#|\Z)', md, re.S)
    if mm:
        meta = esc_text(mm.group(1)).replace('\n> ', '<br>').replace('\n>', '<br>')
    toc_html = '<nav class="toc"><h4>目录</h4>'
    for lv, hid, txt in toc:
        toc_html += '<a class="lv%d" href="#%s">%s</a>' % (lv, hid, txt)
    toc_html += '</nav>'
    doc = ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>%s</title><style>%s</style></head><body><div class="wrap">%s'
           '<main><header class="cover"><h1>%s</h1><div class="meta">%s</div></header>'
           '%s<footer>本预览版由教材 Markdown 自动生成，供团队评审。代码块右上角可一键复制。</footer>'
           '</main></div>%s</body></html>') % (title, CSS, toc_html, title, meta, body, JS)
    open(html_path, 'w', encoding='utf-8').write(doc)
    print('OK', os.path.basename(html_path), len(doc), 'bytes, TOC items', len(toc))

if __name__ == '__main__':
    try:
        log("START")
        for md, html in FILES:
            log("BUILD " + md)
            build(md, html)
            log("DONE " + html)
        log("ALL DONE")
    except Exception as e:
        import traceback
        log("EXCEPTION")
        open(r"C:/Users/sghpe/Desktop/BaiduSyncdisk/两本教材/_err.log", "w", encoding="utf-8").write(traceback.format_exc())
