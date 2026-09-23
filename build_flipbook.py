# -*- coding: utf-8 -*-
"""把教材 Markdown 编译为单文件互动翻页 HTML（零依赖、双击即开）。

每个模块内容按小节性质归为三段：
    传道·授业（讲授） / 思想·碰撞（讨论） / 实验·复现（实验）
三段内各自从 1 重新编号；每页页脚配一条与当页关键词关联的名人名言。

用法：
    python build_flipbook.py                 # 从整本 md 生成两本
    python build_flipbook.py --plan          # 只打印归类映射表
    python build_flipbook.py --src src --book dsdh   # 从 src/ 单本重建《数据科学与数字人文》
    python build_flipbook.py --src src --book ar     # 从 src/ 单本重建《档案智能管理》

说明：
    --src 模式把 src/ 下 NN_*.md 按文件名排序拼成一本临时 md，再走与「整本 md」
    完全相同的编译流程；因此 GitHub Pages 可由可编辑的 src/ 自动重建 book.html。
"""
import re, os, sys, json, random, base64

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_html as bh            # 复用 Markdown 渲染
from quotes_bank import QUOTES

SEED = 20260909
BUDGET = 720        # 每页正文预算（字符）；16:9 短屏下控制在一屏可读范围
MIN_SPLIT = 300     # 当前页已有此长度时，新小节另起一页

PARTS = [
    ('teach', '传道·授业', '课堂讲授', '#1F2A44'),
    ('talk',  '思想·碰撞', '课堂讨论', '#9E2B25'),
    ('lab',   '实验·复现', '课堂实验', '#3F6B57'),
]
PART_COLOR = {k: c for k, _, _, c in PARTS}
PART_NAME = {k: n for k, n, _, _ in PARTS}

# —— 归类规则 ——
LAB_KW = ['实操', '实验', '动手', '复现', '上机', '练习', '操作', '环境搭建', '安装', '运行',
          '评价量规', '实验任务', '量规', '综合实践', '综合项目', '实践项目', '真实操作',
          '案例精读', '第一次动手', '项目实践', '实训', '演练', '工作台', '工作流',
          '任务与评价', '实践路径', '实践：', '实践:', '实现', '搭建', '选题与需求分析',
          '系统设计', '成果展示', '答辩', '步骤', '工具']
TALK_KW = ['思考与讨论', '思考题', '讨论', '思政', '批判', '伦理', '争鸣', '反思', '辩论',
           '挑战', '争议', '风险', '边界', '现实案例', '课程反思', '学术诚信', '科研伦理',
           '畅想', '展望', '争议与', '坐标', '对话', '问答']
# 强制归入「实验·复现」（用户指定：学术前沿与核心期刊文献实证移到实验段）
LAB_FORCE = ['学术前沿', '中文核心期刊文献实证']
# 讲授型小节（无论正文含什么内容，一律归入「传道·授业」）
TEACH_LOCK = ['知识库延展', '参考文献', '前沿瞭望', '本章小结', '学习路径', '全书面貌',
              '引言', '历程', '概念', '理论']
# 正文中的操作性痕迹
OP_RE = re.compile(r'步骤|命令行|pip install|运行以下|在终端|import |提示词|实操|动手|复现|'
                   r'执行|调用|代码|脚本|工具链|操作流程|打开文件|新建|点击')
# 需要删除的提示性字样
PROMPT_RE = re.compile(r'^[^\S\n]*(?:用一句话收束(?:本模块|本章)|一句话收束)[：:]?\s*', re.M)

CHAPTER_SKIP = ['教材总体结构', '实施策略', '多模态内容层次架构', '版权保护与标准建设',
                '推广与应用策略', '附录']
CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8,
      '九': 9, '十': 10, '十一': 11, '十二': 12, '十三': 13}


def classify(title, body=''):
    t = title
    if any(k in t for k in LAB_FORCE):
        return 'lab'
    lab_hit = any(k in t for k in LAB_KW)
    talk_hit = any(k in t for k in TALK_KW)
    if talk_hit and not lab_hit:
        return 'talk'
    if lab_hit:
        return 'lab'
    if any(k in t for k in TEACH_LOCK):
        return 'teach'
    if body:
        if '```' in body:
            return 'lab'
        if len(OP_RE.findall(body)) >= 3:
            return 'lab'
    return 'teach'


def chapter_label(title):
    m = re.search(r'模块(十[一二]?|[一二三四五六七八九])\s', title)
    if m:
        return '模块' + m.group(1)
    m = re.search(r'第(十[一二]?|[一二三四五六七八九])部分', title)
    if m:
        return '第' + m.group(1) + '部分'
    return title.strip()


def clean_title(t):
    """去掉原有编号体系（1.2 / 12.11 / 综合.4 / 模块三·），只留标题文字。"""
    t = re.sub(r'^\s*模块[^\s·]*·\s*', '', t)
    t = re.sub(r'^\s*(?:综合\.)?\d+(?:\.\d+)*\s*[．.、]?\s*[　\s]*', '', t)
    return t.strip() or t


def fullwidth_quotes(md):
    """正文（非代码块）中的直引号转为全角引号。"""
    out, in_code = [], False
    for ln in md.split('\n'):
        if ln.lstrip().startswith('```'):
            in_code = not in_code
            out.append(ln); continue
        if in_code or ln.startswith(('    ', '\t')):
            out.append(ln); continue
        parts = re.split(r'(`[^`]+`)', ln)
        buf = []
        for p in parts:
            if len(p) >= 2 and p.startswith('`') and p.endswith('`'):
                buf.append(p)
            else:
                s, i = [], 0
                for ch in p:
                    if ch == '"':
                        s.append('\u201c' if i % 2 == 0 else '\u201d'); i += 1
                    else:
                        s.append(ch)
                buf.append(''.join(s))
        out.append(''.join(buf))
    return '\n'.join(out)


def parse_book(path):
    md = fullwidth_quotes(open(path, encoding='utf-8').read())
    lines = md.split('\n')
    chapters = []
    cur = None
    buf = []
    sec_no = ''
    sec_title = ''
    in_sec = False

    def flush():
        nonlocal buf
        if in_sec:
            body = PROMPT_RE.sub('', '\n'.join(buf).strip())
            cur['sections'].append({'no': sec_no, 'title': sec_title, 'body': body})
        buf = []

    for ln in lines:
        if ln.startswith('## '):
            flush(); in_sec = False
            title = ln[3:].strip()
            if any(s in title for s in CHAPTER_SKIP):
                cur = None
                continue
            cur = {'title': title, 'label': chapter_label(title), 'sections': []}
            chapters.append(cur)
            continue
        if cur is None:
            continue
        if ln.startswith('### '):
            flush()
            head = ln[4:].strip()
            m = re.match(r'^([\d.]+\d|综合\.\d+)\s*(.*)$', head)
            if m and not head.startswith('模块'):
                sec_no = m.group(1)
                rest = m.group(2)
            else:
                mm = re.match(r'^模块[^\s·]*·\s*(.*)$', head)
                sec_no = ''
                rest = mm.group(1) if mm else head
            sec_title = (sec_no + '　' + rest).strip() if sec_no else rest
            sec_title = re.sub(r'^[:：\s]+', '', sec_title)
            in_sec = True
            buf = []
            continue
        if in_sec:
            buf.append(ln)
    flush()
    return chapters


# ---------- 分页 ----------
TABLE_MAX = 780


def split_table(lines):
    """超长表格按行切成多块（每块自带表头），避免单页塞不下。"""
    body = '\n'.join(lines)
    if len(body) <= TABLE_MAX or len(lines) < 4:
        return [body]
    head = lines[:2]          # 表头 + 分隔行
    rows = lines[2:]
    chunks, cur, curlen = [], [], 0
    for r in rows:
        cur.append(r); curlen += len(r)
        if curlen >= TABLE_MAX:
            chunks.append('\n'.join(head + cur)); cur, curlen = [], 0
    if cur:
        chunks.append('\n'.join(head + cur))
    return chunks


def is_special(l):
    return (l.startswith('#') or l.startswith('>') or l.startswith('```') or
            re.match(r'^\s*-\s+', l) or re.match(r'^\s*\d+\.\s+', l) or
            re.match(r'^\s*\|', l) or l.strip() == '')


def md_blocks(body):
    lines = body.split('\n')
    i, out = 0, []
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        if ln.startswith('```'):
            buf = [ln]; i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                buf.append(lines[i]); i += 1
            if i < len(lines):
                buf.append(lines[i]); i += 1
            out.append('\n'.join(buf)); continue
        if ln.startswith('>'):
            buf = []
            while i < len(lines) and lines[i].startswith('>'):
                buf.append(lines[i]); i += 1
            out.append('\n'.join(buf)); continue
        if re.match(r'^\s*\|', ln):
            buf = []
            while i < len(lines) and (re.match(r'^\s*\|', lines[i]) or
                                      re.match(r'^\s*\|?[\s:|\-]+\|?\s*$', lines[i])):
                buf.append(lines[i]); i += 1
            out.extend(split_table(buf)); continue
        if re.match(r'^\s*-\s+', ln) or re.match(r'^\s*\d+\.\s+', ln):
            buf = []
            while i < len(lines) and (re.match(r'^\s*-\s+', lines[i]) or
                                      re.match(r'^\s*\d+\.\s+', lines[i]) or
                                      (lines[i].startswith(('  ', '\t')) and lines[i].strip())):
                buf.append(lines[i]); i += 1
            out.append('\n'.join(buf)); continue
        if ln.startswith('#'):
            out.append(ln); i += 1; continue
        buf = []
        while i < len(lines) and lines[i].strip() and not is_special(lines[i]):
            buf.append(lines[i]); i += 1
        out.append('\n'.join(buf))
    # 把「短导语段」与其后的表格/代码块绑定成一个整体，避免导语被单独切成一页
    merged, i = [], 0
    while i < len(out):
        b = out[i]
        nxt = out[i + 1] if i + 1 < len(out) else ''
        if (nxt and len(b) < 260 and not b.startswith('```') and not b.lstrip().startswith('|')
                and (nxt.startswith('```') or nxt.lstrip().startswith('|'))):
            merged.append(b + '\n\n' + nxt); i += 2
        else:
            merged.append(b); i += 1
    return merged


def render(md):
    html = bh.convert(md)[0]
    html = (html.replace('<table>', '<div class="tablewrap"><table>')
                .replace('</table>', '</table></div>'))
    return html


# ---------- 图片内嵌（单文件离线） ----------
IMG_EXT = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
           '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml',
           '.bmp': 'image/bmp'}


def embed_images(html, base_dir):
    """把 HTML 中本地路径的 <img src> 转成 base64 data URI，保持单文件离线。
    已为 data:/http(s) 的不动；本地文件缺失则告警并保留原 src（预览时显示破图）。"""
    def rep(m):
        src = m.group(1)
        if src.startswith(('data:', 'http://', 'https://', '//', '#')):
            return m.group(0)
        p = src if os.path.isabs(src) else os.path.join(base_dir, src)
        if not os.path.exists(p):
            print('  [warn] 图片缺失，未内嵌：', src)
            return m.group(0)
        ext = os.path.splitext(p)[1].lower()
        mime = IMG_EXT.get(ext, 'image/png')
        b64 = base64.b64encode(open(p, 'rb').read()).decode()
        return 'src="data:%s;base64,%s"' % (mime, b64)
    return re.sub(r'src="([^"]+)"', rep, html)


def render_embed(md, base_dir=HERE):
    return embed_images(render(md), base_dir)


def first_module_image(ch, base_dir=HERE):
    """取模块内第一张本地图片并内嵌，用作模块封面图（无则返回空串）。"""
    for s in ch['sections']:
        mm = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', s['body'])
        if mm:
            alt, src = mm.group(1), mm.group(2)
            if src.startswith(('data:', 'http://', 'https://', '//')):
                continue
            p = src if os.path.isabs(src) else os.path.join(base_dir, src)
            if os.path.exists(p):
                ext = os.path.splitext(p)[1].lower()
                mime = IMG_EXT.get(ext, 'image/png')
                b64 = base64.b64encode(open(p, 'rb').read()).decode()
                return ('<figure class="coverimg"><img src="data:%s;base64,%s" alt="%s">'
                        '<figcaption>%s</figcaption></figure>'
                        % (mime, b64, bh.esc_text(alt), bh.esc_text(alt)))
    return ''


# ---------- 名言匹配 ----------
def pick_quote(title, text, used, rnd, recent=None):
    """按关键词打分选名言；recent 为最近若干页已用索引，强制避开以免相邻页重复。"""
    recent = recent or set()
    best, bs, btag = 0, -99, ''
    fallback, fb = 0, -99
    for idx, (q, a, tags) in enumerate(QUOTES):
        s, hit = 0.0, ''
        for t in tags:
            if t in title:
                s += 3.0
                if not hit:
                    hit = t
            elif t in text:
                s += 1.0
                if not hit:
                    hit = t
        s -= used.get(idx, 0) * 2.2
        s += rnd.random() * 0.5
        if idx not in recent and s > bs:
            bs, best, btag = s, idx, hit
        if s > fb:
            fb, fallback = s, idx
    if bs == -99:
        best, btag = fallback, ''
    used[best] = used.get(best, 0) + 1
    q, a, _ = QUOTES[best]
    return q, a, (btag or ''), best


# ---------- HTML 模板 ----------
TPL = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--ink:#1F2A44;--paper:#FBF9F4;--bg:#EDE9E0;--seal:#9E2B25;--slate:#5B6B8C;
--line:#DEd8CA;--teach:#1F2A44;--talk:#9E2B25;--lab:#3F6B57;}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{background:var(--bg);color:var(--ink);
font-family:"Source Han Serif SC","Noto Serif CJK SC","Songti SC",SimSun,serif;
-webkit-font-smoothing:antialiased;overflow:hidden}
.ui{font-family:"Microsoft YaHei","PingFang SC",-apple-system,"Segoe UI",sans-serif}
.app{display:flex;flex-direction:column;height:100vh}
.topbar{display:flex;align-items:center;gap:12px;padding:9px 18px;background:#1F2A44;color:#F3EFE6;
box-shadow:0 2px 10px rgba(31,42,68,.25);z-index:20}
.topbar .bk{font-size:15px;font-weight:700;letter-spacing:.5px}
.topbar .crumb{font-size:12.5px;color:#C9C3B6;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tbtn{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);color:#F3EFE6;
border-radius:6px;padding:5px 11px;font-size:12.5px;cursor:pointer;white-space:nowrap}
.tbtn:hover{background:rgba(255,255,255,.18)}
.jump{width:56px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);
color:#F3EFE6;border-radius:6px;padding:5px 7px;font-size:12.5px;text-align:center}
.bar{height:3px;background:#D9D3C5}
.bar i{display:block;height:100%;width:0;background:var(--seal);transition:width .25s}
.stage{flex:1;position:relative;display:flex;align-items:center;justify-content:center;padding:22px 72px;overflow:hidden}
.hit{position:absolute;top:0;bottom:0;width:72px;cursor:pointer;z-index:5;display:flex;align-items:center;justify-content:center;
color:#B9B2A2;font-size:30px;user-select:none;transition:.2s}
.hit:hover{color:var(--seal);background:rgba(158,43,37,.05)}
.hit.l{left:0}.hit.r{right:0}
.sheet{background:var(--paper);border:1px solid var(--line);
border-radius:4px;box-shadow:0 10px 34px rgba(31,42,68,.16);display:flex;flex-direction:column;overflow:hidden}
.sheet.anim{animation:fade .26s ease}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.shead{padding:18px 42px 11px;border-bottom:1px solid var(--line);flex-shrink:0}
.shead .tag{display:inline-block;font-size:12px;padding:3px 10px;border-radius:20px;color:#fff;margin-bottom:7px}
.shead h2{font-size:21px;line-height:1.45;font-weight:700}
.shead .sub{font-size:12.5px;color:var(--slate);margin-top:5px}
.sbody{flex:1;overflow-y:auto;padding:13px 42px 18px;font-size:15.2px;line-height:1.82}
.sbody::-webkit-scrollbar{width:7px}
.sbody::-webkit-scrollbar-thumb{background:#D6CFC0;border-radius:4px}
.sbody h3{font-size:16.5px;margin:14px 0 7px;color:var(--ink)}
.sbody h4{font-size:15px;margin:13px 0 6px;color:var(--slate);font-weight:700}
.sbody p{margin:7px 0;text-align:justify}
.sbody ul,.sbody ol{margin:7px 0 7px 22px}
.sbody li{margin:3px 0}
.sbody blockquote{margin:10px 0;padding:9px 15px;background:#F4F1E8;border-left:3px solid var(--seal);
color:#3B3B3B;font-size:14px;line-height:1.8}
.sbody blockquote p{margin:3px 0}
.sbody code{background:#F0EDE4;padding:1px 5px;border-radius:3px;font-size:13px;
font-family:Consolas,"Courier New",monospace}
.codewrap{position:relative;margin:10px 0}
.codewrap pre{background:#F4F1E8;border-left:3px solid var(--slate);padding:10px 13px;overflow-x:auto;
font-size:12.6px;line-height:1.62;font-family:Consolas,"Courier New",monospace}
.copybtn{position:absolute;right:7px;top:5px;font-size:11.5px;background:#fff;border:1px solid var(--line);
border-radius:4px;padding:2px 8px;cursor:pointer;color:var(--slate)}
.tablewrap{overflow-x:auto;margin:10px 0}
.sbody table{border-collapse:collapse;width:100%;font-size:12.6px;line-height:1.55}
.sbody th,.sbody td{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}
.sbody th{background:#EFEBE2;font-weight:700}
.sbody a{color:var(--seal);word-break:break-all}
.sbody hr{border:0;border-top:1px solid var(--line);margin:13px 0}
.sfoot{border-top:1px solid var(--line);padding:10px 42px 12px;background:#F7F4EC;font-size:13px;color:#4A4A4A;
display:flex;gap:10px;align-items:flex-start;flex-shrink:0}
.sfoot .qt{flex:1;font-style:italic;line-height:1.65}
.sfoot .au{color:var(--seal);font-style:normal;font-weight:700}
.sfoot .kw{font-size:11px;border:1px solid var(--line);border-radius:10px;padding:1px 9px;color:var(--slate);
white-space:nowrap;background:#fff}
/* 图片：点击放大 + 模块封面 */
.sbody img{cursor:zoom-in;max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px}
.coverimg{margin:14px 0 4px;text-align:center}
.coverimg img{max-width:248px;border-radius:8px;box-shadow:0 4px 16px rgba(31,42,68,.2)}
.coverimg figcaption{font-size:12px;color:var(--slate);margin-top:5px}
.lb{position:fixed;inset:0;background:rgba(18,20,28,.92);z-index:60;display:none;
align-items:center;justify-content:center}
.lb.on{display:flex}
.lbmid{display:flex;flex-direction:column;align-items:center;max-width:94vw;max-height:88vh}
.lb img{max-width:94vw;max-height:80vh;border-radius:6px;box-shadow:0 12px 40px rgba(0,0,0,.5)}
.lb .cap{color:#E6E0D3;font-size:13.5px;margin-top:10px;text-align:center;max-width:80vw}
.lb .lbcnt{color:#9A9488;font-size:12px;margin-top:4px}
.lbnav{position:absolute;top:50%;transform:translateY(-50%);background:rgba(255,255,255,.12);
border:1px solid rgba(255,255,255,.2);color:#F3EFE6;font-size:30px;border-radius:50%;width:48px;height:48px;cursor:pointer}
.lbnav:hover{background:rgba(255,255,255,.25)}
.lbnav.l{left:18px}.lbnav.r{right:18px}
.lbclose{position:absolute;top:16px;right:18px;background:rgba(255,255,255,.12);
border:1px solid rgba(255,255,255,.2);color:#F3EFE6;font-size:13px;padding:6px 12px;border-radius:6px;cursor:pointer}
/* 封面 / 分隔页 */
.sheet.dark{background:#1F2A44;color:#F3EFE6;border-color:#1F2A44}
.sheet.dark .sbody{color:#E6E0D3}
.sheet.dark .sbody h3,.sheet.dark .sbody h4{color:#F3EFE6}
.sheet.dark .sbody blockquote{background:rgba(255,255,255,.06);border-left-color:#C8A2A0;color:#E6E0D3}
.sheet.dark .sbody code{background:rgba(255,255,255,.08);color:#E6E0D3}
.sheet.dark .codewrap pre{background:rgba(255,255,255,.06);color:#E6E0D3}
.sheet.dark .sbody th{background:rgba(255,255,255,.08)}
.sheet.dark .sbody th,.sheet.dark .sbody td{border-color:rgba(255,255,255,.18)}
.sheet.dark .sfoot{background:rgba(0,0,0,.18);border-top-color:rgba(255,255,255,.15);color:#CFC9BC}
.shead.big{padding:52px 54px;border:0}
.shead.big .num{font-size:13px;letter-spacing:4px;color:#C9C3B6;margin-bottom:12px}
.shead.big h1{font-size:36px;line-height:1.4}
.agenda{padding:6px 54px 26px;font-size:14px;line-height:1.95}
.agenda .grp{margin-top:12px}
.agenda .grp .nm{font-weight:700;font-size:13.5px;margin-bottom:2px}
.agenda .grp ol{margin-left:20px;color:#CFC9BC}
.pnl{margin:14px 0 4px 22px;font-size:14.5px;line-height:1.95}
.pnl li{margin:4px 0}
/* 目录抽屉 */
.mask{position:fixed;inset:0;background:rgba(20,20,20,.45);z-index:40;display:none}
.mask.on{display:block}
.toc{position:fixed;left:0;top:0;bottom:0;width:min(430px,88vw);background:#FBF9F4;z-index:50;
box-shadow:6px 0 30px rgba(0,0,0,.25);transform:translateX(-102%);transition:transform .28s;
display:flex;flex-direction:column}
.toc.on{transform:none}
.toc .th{padding:16px 20px;background:#1F2A44;color:#F3EFE6;font-size:15px;font-weight:700;
display:flex;justify-content:space-between;align-items:center}
.toc .th span{font-size:12px;font-weight:400;color:#C9C3B6}
.toc .tb{flex:1;overflow-y:auto;padding:10px 14px 30px}
.toc .ch{margin:10px 0 4px;font-weight:700;font-size:14px;color:var(--ink);cursor:pointer;
padding:6px 8px;border-radius:5px}
.toc .ch:hover{background:#F0EDE4}
.toc .pt{font-size:12.5px;padding:3px 8px 3px 18px;font-weight:700}
.toc .sec{font-size:13px;padding:4px 8px 4px 30px;color:#444;cursor:pointer;border-radius:4px;
overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.toc .sec:hover{background:#F2EEE4;color:var(--seal)}
.toc .empty{font-size:12px;color:#A8A196;padding:2px 8px 2px 30px}
.hint{position:fixed;right:16px;bottom:10px;font-size:11.5px;color:#9A9488;z-index:10}
@media(max-width:820px){.stage{padding:10px 44px}.shead{padding:13px 20px 9px}
.sbody{padding:11px 20px 15px;font-size:15px}.sfoot{padding:8px 20px 10px}
.shead.big{padding:36px 24px}.shead.big h1{font-size:26px}.agenda{padding:4px 24px 18px}
.pnl{margin-left:18px}.hit{width:44px}.topbar{gap:7px;padding:8px 10px}.topbar .crumb{display:none}}
</style>
</head>
<body>
<div class="app">
  <div class="topbar ui">
    <button class="tbtn" id="btnToc">☰ 目录</button>
    <button class="tbtn" id="btnFs">⛶ 全屏</button>
    <div class="bk">__TITLE__</div>
    <div class="crumb" id="crumb"></div>
    <input class="jump ui" id="jump" type="text" placeholder="页码">
    <div class="ui" id="pager" style="font-size:12.5px;color:#C9C3B6;min-width:62px;text-align:right"></div>
  </div>
  <div class="bar"><i id="prog"></i></div>
  <div class="stage" id="stage">
    <div class="hit l ui" id="hl">‹</div>
    <article class="sheet" id="sheet">
      <div class="shead" id="shead"></div>
      <div class="sbody" id="sbody"></div>
      <div class="sfoot" id="sfoot"></div>
    </article>
    <div class="hit r ui" id="hr">›</div>
  </div>
</div>
<div class="mask" id="mask"></div>
<nav class="toc" id="toc">
  <div class="th ui"><span>__TITLE__</span><button class="tbtn" id="btnClose">关闭 ✕</button></div>
  <div class="tb" id="tocBody"></div>
</nav>
<div class="hint ui">← → 翻页 · 空格前进 · T 目录 · F 全屏 · 点击图片放大 · Home/End 首尾</div>
<div class="lb" id="lb">
  <button class="lbnav l ui" id="lbPrev">‹</button>
  <div class="lbmid"><img id="lbImg" alt=""><div class="cap" id="lbCap"></div><div class="lbcnt ui" id="lbCount"></div></div>
  <button class="lbnav r ui" id="lbNext">›</button>
  <button class="lbclose ui" id="lbClose">✕ 关闭</button>
</div>
<script>
const PAGES = __PAGES__;
const CH = __CH__;
const KEY = "__KEY__";
let cur = 0;
try{const s=+localStorage.getItem(KEY); if(s&&s<PAGES.length) cur=s;}catch(e){}
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const PCOL={teach:'#1F2A44',talk:'#9E2B25',lab:'#3F6B57'};
const PNM={teach:'传道·授业',talk:'思想·碰撞',lab:'实验·复现'};

function buildToc(){
  let h='';
  CH.forEach(c=>{
    h+='<div class="ch ui" data-p="'+c.p+'">'+esc(c.t)+'</div>';
    ['teach','talk','lab'].forEach(k=>{
      const arr=c[k]||[];
      h+='<div class="pt ui" style="color:'+PCOL[k]+'">'+PNM[k]+'（'+arr.length+'）</div>';
      if(!arr.length) h+='<div class="empty">— 本模块该部分暂无独立小节 —</div>';
      arr.forEach(s=>{h+='<div class="sec" data-p="'+s.p+'">'+esc(s.t)+'</div>';});
    });
  });
  $('tocBody').innerHTML=h;
  $('tocBody').querySelectorAll('[data-p]').forEach(el=>{el.onclick=()=>{go(+el.dataset.p);closeToc();};});
}
function fitStage(){
  const st=$('stage'); const sheet=$('sheet');
  const cs=getComputedStyle(st);
  const availW=st.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
  const availH=st.clientHeight-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom);
  let w=availW, h=w*9/16;
  if(h>availH){ h=availH; w=h*16/9; }
  sheet.style.width=Math.floor(w)+'px';
  sheet.style.height=Math.floor(h)+'px';
}
function fit(){
  const b=$('sbody');
  b.style.fontSize='';
  let s=1.0, guard=0;
  while(b.scrollHeight>b.clientHeight+2 && s>0.74 && guard++<14){
    s-=0.02; b.style.fontSize=(15.2*s).toFixed(2)+'px';
  }
}
function go(i){
  if(i<0) i=0; if(i>=PAGES.length) i=PAGES.length-1;
  cur=i;
  try{localStorage.setItem(KEY,cur);}catch(e){}
  const p=PAGES[i];
  const sh=$('shead'), sheet=$('sheet');
  sheet.classList.remove('dark'); sh.className='shead';
  if(p.k==='cover'){
    sh.classList.add('big');
    sh.innerHTML='<h1>'+esc(p.t)+'</h1>';
  }else if(p.k==='chap'){
    sheet.classList.add('dark'); sh.classList.add('big');
    sh.innerHTML='<div class="num ui">'+esc(p.m)+'</div><h1>'+esc(p.t)+'</h1>';
  }else if(p.k==='part'){
    sh.innerHTML='<span class="tag ui" style="background:'+(p.c||'#1F2A44')+'">'+esc(p.pn)+'</span>'+
      '<h2>'+esc(p.t)+'</h2><div class="sub">'+esc(p.m)+' · 共 '+p.cnt+' 节</div>';
  }else{
    sh.innerHTML='<span class="tag ui" style="background:'+(p.c||'#1F2A44')+'">'+esc(p.pn)+'</span>'+
      '<h2>'+esc(p.t)+'</h2><div class="sub">'+esc(p.m)+' · '+esc(p.n)+'</div>';
  }
  let body=p.b||'';
  if(p.k==='chap') body='<div class="agenda ui">'+body+'</div>';
  $('sbody').innerHTML=body;
  $('sfoot').innerHTML = p.q ? ('<span class="qt">「'+esc(p.q)+'」<span class="au"> —— '+esc(p.a)+'</span></span>'+
      (p.g?'<span class="kw ui">'+esc(p.g)+'</span>':'')) : '';
  $('crumb').textContent = p.cr||'';
  $('pager').textContent = (i+1)+' / '+PAGES.length;
  $('prog').style.width = ((i+1)/PAGES.length*100)+'%';
  sheet.classList.remove('anim'); void sheet.offsetWidth; sheet.classList.add('anim');
  fitStage();
  $('sbody').scrollTop=0;
  fit();
}
function next(){go(cur+1)} function prev(){go(cur-1)}
function openToc(){$('toc').classList.add('on');$('mask').classList.add('on')}
function closeToc(){$('toc').classList.remove('on');$('mask').classList.remove('on')}
function toggleFs(){
  if(!document.fullscreenElement){
    if(document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
  }else{
    if(document.exitFullscreen) document.exitFullscreen();
  }
}
$('hl').onclick=prev; $('hr').onclick=next;
$('btnToc').onclick=openToc; $('btnClose').onclick=closeToc; $('mask').onclick=closeToc;
$('btnFs').onclick=toggleFs;
$('jump').onkeydown=e=>{if(e.key==='Enter'){const v=parseInt($('jump').value,10);
  if(v>=1&&v<=PAGES.length){go(v-1);closeToc();}$('jump').value='';}};
window.addEventListener('resize',()=>{fitStage();fit();});
document.addEventListener('keydown',e=>{
  if(e.target.tagName==='INPUT') return;
  if($('lb').classList.contains('on')){
    if(e.key==='ArrowLeft'||e.key==='PageUp'){lbStep(-1);e.preventDefault();}
    else if(e.key==='ArrowRight'||e.key==='PageDown'){lbStep(1);e.preventDefault();}
    else if(e.key==='Escape'){closeLb();}
    return;
  }
  if(e.key==='ArrowRight'||e.key==='PageDown'){next();e.preventDefault();}
  else if(e.key==='ArrowLeft'||e.key==='PageUp'){prev();e.preventDefault();}
  else if(e.key===' '){next();e.preventDefault();}
  else if(e.key==='Home'){go(0);e.preventDefault();}
  else if(e.key==='End'){go(PAGES.length-1);e.preventDefault();}
  else if(e.key==='t'||e.key==='T'){ $('toc').classList.contains('on')?closeToc():openToc(); }
  else if(e.key==='f'||e.key==='F'){ toggleFs(); }
  else if(e.key==='Escape'){closeToc();}
});
function copyCode(b){
  const pre=b.parentNode.querySelector('pre');
  const t=document.createRange(); t.selectNodeContents(pre);
  const sel=window.getSelection(); sel.removeAllRanges(); sel.addRange(t);
  try{document.execCommand('copy'); b.textContent='已复制';}catch(e){b.textContent='复制失败';}
  setTimeout(()=>{b.textContent='复制';},1500);
}
let lbList=[], lbIdx=0;
function openLb(img){
  lbList=Array.from($('sbody').querySelectorAll('img'));
  lbIdx=lbList.indexOf(img); if(lbIdx<0) lbIdx=0;
  showLb(); $('lb').classList.add('on');
}
function showLb(){
  const img=lbList[lbIdx]; if(!img) return;
  $('lbImg').src=img.src;
  const fig=img.closest('figure');
  $('lbCap').textContent=fig&&fig.querySelector('figcaption')?fig.querySelector('figcaption').textContent:'';
  $('lbCount').textContent=(lbIdx+1)+' / '+lbList.length;
}
function lbStep(d){ if(!lbList.length) return; lbIdx=(lbIdx+d+lbList.length)%lbList.length; showLb(); }
function closeLb(){ $('lb').classList.remove('on'); }
$('sbody').addEventListener('click',e=>{ if(e.target&&e.target.tagName==='IMG') openLb(e.target); });
$('lb').addEventListener('click',e=>{ if(e.target.id==='lb'||e.target.id==='lbClose') closeLb(); });
$('lbPrev').onclick=e=>{e.stopPropagation();lbStep(-1);};
$('lbNext').onclick=e=>{e.stopPropagation();lbStep(1);};
buildToc(); go(cur);
</script>
</body>
</html>
"""


def pack_pages(arr, budget=BUDGET):
    """把一个「部分」内的小节打包成若干页，避免只有标题的空页。"""
    flat = []
    sec_len = {}
    for si, s in enumerate(arr):
        blocks = md_blocks(s['body'])
        sec_len[si] = sum(len(b) for b in blocks) + len(clean_title(s['title']))
        flat.append({'md': '#### %d　%s' % (si + 1, clean_title(s['title'])),
                     'is_head': True, 'si': si})
        for b in blocks:
            flat.append({'md': b, 'is_head': False, 'si': si})
    out, cur, curlen, cursecs = [], [], 0, []
    for it in flat:
        if it['is_head']:
            # 只有当前页确实装不下这一整节时才另起一页，避免出现「标题+脚注」的近空页
            if cur and curlen + sec_len[it['si']] > budget:
                out.append((cur, cursecs)); cur, curlen, cursecs = [], 0, []
            cur.append(it)
            if it['si'] not in cursecs:
                cursecs.append(it['si'])
            curlen += len(it['md'])
            continue
        L = len(it['md'])
        # 只有当前页已有足够内容（≥300 字符）时才切页，避免留下近空页
        if cur and curlen + L > budget and curlen >= 300:
            out.append((cur, cursecs)); cur, curlen, cursecs = [], 0, []
        cur.append(it)
        if it['si'] not in cursecs:
            cursecs.append(it['si'])
        curlen += L
        if curlen >= budget:
            out.append((cur, cursecs)); cur, curlen, cursecs = [], 0, []
    if cur:
        out.append((cur, cursecs))
    return out


def build(md_path, out_path, title, key):
    chapters = parse_book(md_path)
    rnd = random.Random(SEED)
    used = {}
    pages = []
    ch_nav = []
    recent = []

    def PQ(title_, text):
        q, a, g, idx = pick_quote(title_, text, used, rnd, set(recent))
        recent.append(idx)
        if len(recent) > 18:
            recent.pop(0)
        return q, a, g

    q, a, g = PQ('教育 学习 人文 数据', title)
    pages.append({'k': 'cover', 't': title, 'm': '', 'pn': '', 'c': '', 'n': '',
                  'b': '', 'q': q, 'a': a, 'g': g, 'cr': '封面'})

    for ch in chapters:
        parts = {'teach': [], 'talk': [], 'lab': []}
        for s in ch['sections']:
            parts[classify(s['title'], s['body'])].append(s)
        short = re.sub(r'^(模块[^\s]*|第[^\s]*部分)\s*', '', ch['title'])
        nav = {'t': ch['label'] + '　' + short, 'p': len(pages)}

        q, a, g = PQ(ch['title'], ch['title'])
        cover = first_module_image(ch)
        agenda = cover
        for k, nm, _, col in PARTS:
            arr = parts[k]
            if not arr:
                continue
            agenda += ('<div class="grp"><div class="nm" style="color:%s">%s · %d 节</div><ol>%s</ol></div>'
                       % (col, nm, len(arr),
                          ''.join('<li>%d　%s</li>' % (i + 1, bh.esc_text(clean_title(x['title'])))
                                  for i, x in enumerate(arr))))
        pages.append({'k': 'chap', 't': short, 'm': ch['label'], 'pn': '', 'c': '', 'n': '',
                      'b': agenda, 'q': q, 'a': a, 'g': g,
                      'cr': ch['label'] + ' · 本模块导览'})
        ch_nav.append(nav)

        for k, nm, _, col in PARTS:
            arr = parts[k]
            nav[k] = []
            if not arr:
                continue
            q, a, g = PQ(nm + ' ' + ch['title'], ch['title'])
            outline = ('<ol class="pnl">%s</ol>'
                       % ''.join('<li>%d　%s</li>' % (i + 1, bh.esc_text(clean_title(x['title'])))
                                 for i, x in enumerate(arr)))
            pages.append({'k': 'part', 't': nm, 'm': ch['label'] + '　' + short,
                          'pn': nm, 'c': col, 'cnt': len(arr), 'n': '',
                          'b': outline, 'q': q, 'a': a, 'g': g,
                          'cr': ch['label'] + ' · ' + nm})
            packed = pack_pages(arr)
            seen = {}
            last_ptitle = None
            for items, secs in packed:
                nums = [s + 1 for s in secs]
                nlab = ('第 %d 节' % nums[0]) if len(nums) == 1 else \
                       ('第 %d–%d 节' % (nums[0], nums[-1]))
                head_title = clean_title(arr[secs[0]]['title'])
                ptitle = '%d　%s' % (nums[0], head_title)
                ptitle_disp = ptitle + '（续）' if ptitle == last_ptitle else ptitle
                last_ptitle = ptitle
                body_md, started = [], False
                for it in items:
                    if it['is_head'] and not started:
                        started = True
                        continue
                    body_md.append(it['md'])
                plain = re.sub(r'[#*`>\-\|]', ' ', '\n\n'.join(body_md))
                q, a, g = PQ(head_title + ' ' + nm, plain)
                pidx = len(pages)
                pages.append({'k': 'cont', 't': ptitle_disp, 'm': ch['label'] + '　' + short,
                              'pn': nm, 'c': col, 'n': nlab,
                              'b': render_embed('\n\n'.join(body_md)),
                              'q': q, 'a': a, 'g': g,
                              'cr': ch['label'] + ' · ' + nm + ' · ' + ptitle_disp})
                for s in secs:
                    if s not in seen:
                        seen[s] = pidx
            for si, s in enumerate(arr):
                nav[k].append({'t': '%d　%s' % (si + 1, clean_title(s['title'])),
                               'p': seen.get(si, len(pages) - 1)})

    def dump(o):
        s = json.dumps(o, ensure_ascii=False)
        return (s.replace('</', '<\\/').replace('\u2028', '\\u2028')
                 .replace('\u2029', '\\u2029'))
    html = (TPL.replace('__PAGES__', dump(pages))
               .replace('__CH__', dump(ch_nav))
               .replace('__TITLE__', title)
               .replace('__KEY__', key))
    open(out_path, 'w', encoding='utf-8').write(html)
    stat = {'chapters': len(chapters), 'pages': len(pages),
            'parts': {k: sum(1 for c in ch_nav for _ in c.get(k, [])) for k, _, _, _ in PARTS}}
    return stat, ch_nav


def plan(md_path):
    chapters = parse_book(md_path)
    out = []
    for ch in chapters:
        parts = {'teach': [], 'talk': [], 'lab': []}
        for s in ch['sections']:
            parts[classify(s['title'], s['body'])].append(s['title'])
        out.append((ch['label'], parts))
    return out


def build_from_src(src_dir, out_path, title, key):
    """从 src/ 下 NN_*.md 重建翻页教材（等价于整本 md 直编）。"""
    files = sorted(f for f in os.listdir(src_dir)
                   if re.match(r'^\d+_.*\.md$', f))
    if not files:
        raise SystemExit('src 目录为空或不存在：%s' % src_dir)
    merged = []
    for f in files:
        merged.append(open(os.path.join(src_dir, f), encoding='utf-8').read().rstrip())
    merged_md = '\n\n'.join(merged)
    merged_path = os.path.join(src_dir, '_merged_src.md')
    with open(merged_path, 'w', encoding='utf-8') as fh:
        fh.write(merged_md)
    try:
        return build(merged_path, out_path, title, key)
    finally:
        if os.path.exists(merged_path):
            os.remove(merged_path)


# src 模式：key -> (out_html, title, key)
# out 统一为仓库发布的 book.html（与 index.html 引用一致）
SRC_BOOKS = {
    'dsdh': ('book.html', '《数据科学与数字人文》', 'dsdh_flip_v2'),
    'ar':   ('book.html', '《档案智能管理》', 'ar_flip_v2'),
}


JOBS = [
    ('档案智能管理_智能书编写.md', '档案智能管理_互动翻页教材.html',
     '《档案智能管理》', 'ar_flip_v2'),
    ('数据科学与数字人文_教材编写.md', '数据科学与数字人文_互动翻页教材.html',
     '《数据科学与数字人文》', 'dsdh_flip_v2'),
]

if __name__ == '__main__':
    os.chdir(HERE)
    if '--src' in sys.argv:
        i = sys.argv.index('--src')
        src_dir = sys.argv[i + 1]
        if '--book' not in sys.argv:
            print('用法：python build_flipbook.py --src <dir> --book dsdh|ar')
            sys.exit(1)
        key = sys.argv[sys.argv.index('--book') + 1]
        if key not in SRC_BOOKS:
            print('未知 --book：%s（可选 dsdh / ar）' % key)
            sys.exit(1)
        out, title, k = SRC_BOOKS[key]
        st, _ = build_from_src(src_dir, out, title, k)
        print('%-28s → %-34s 章 %d · 页 %d · 讲授/讨论/实验 = %d/%d/%d'
              % (src_dir, out, st['chapters'], st['pages'],
                 st['parts']['teach'], st['parts']['talk'], st['parts']['lab']))
        sys.exit(0)
    if '--plan' in sys.argv:
        for md, _, t, _ in JOBS:
            print('=' * 60); print(t)
            for label, parts in plan(md):
                print('-' * 50); print(label)
                for k, nm, _, _ in PARTS:
                    print('  [%s] %d 节' % (nm, len(parts[k])))
                    for i, x in enumerate(parts[k]):
                        print('      %d - %s' % (i + 1, x))
        sys.exit(0)
    for md, out, title, key in JOBS:
        st, nav = build(md, out, title, key)
        print('%-28s → %-34s 章 %d · 页 %d · 讲授/讨论/实验 = %d/%d/%d'
              % (md, out, st['chapters'], st['pages'],
                 st['parts']['teach'], st['parts']['talk'], st['parts']['lab']))
