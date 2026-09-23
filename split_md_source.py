# -*- coding: utf-8 -*-
"""把教材 Markdown 按章拆分为可编辑的源文件 src/NN_标题.md（翻页教材的可编辑源）。

设计目标：让 GitHub 仓库里的翻页教材「可被直接修改」。
- 每个 src 文件保留原始的 `## 章节` 标题行及其下全部正文（含 `### 小节`）；
- 被 build_flipbook.parse_book 跳过的章节（CHAPTER_SKIP）不会生成源文件；
- 把同一本书的 src/ 全部文件按文件名排序拼回，喂给 build_flipbook 会得到与
  当前「整本 md 直编」完全一致的翻页教材（章节/分页/名言归类均不变）。

幂等可重跑：重复执行覆盖同名文件，不会产生重复块。

用法：
  python split_md_source.py            # 生成两本书的 src/
  python split_md_source.py --book dsdh  # 只生成《数据科学与数字人文》
  python split_md_source.py --book ar    # 只生成《档案智能管理》
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_flipbook import CHAPTER_SKIP   # 与翻页生成器保持同一跳过清单

BOOKS = [
    ('数据科学与数字人文_教材编写.md', 'dsdh', 'dsdh-pages'),
    ('档案智能管理_智能书编写.md', 'ar', 'air-pages'),
]

BAD = re.compile(r'[\\/:*?"<>|\r\n\t]')


def safe(name):
    name = BAD.sub('_', name).replace('\u3000', ' ')
    return re.sub(r'\s+', ' ', name).strip(' .')


def split(src_md, repo_dir):
    text = open(os.path.join(HERE, src_md), encoding='utf-8').read()
    lines = text.split('\n')
    chapters = []
    cur_title = None
    cur_buf = []
    for ln in lines:
        if ln.startswith('## '):
            if cur_title is not None:
                chapters.append((cur_title, cur_buf))
            title = ln[3:].strip()
            if any(s in title for s in CHAPTER_SKIP):
                cur_title = None
                cur_buf = []
            else:
                cur_title = title
                cur_buf = [ln]
        else:
            if cur_title is not None:
                cur_buf.append(ln)
    if cur_title is not None:
        chapters.append((cur_title, cur_buf))

    out_dir = os.path.join(HERE, repo_dir, 'src')
    os.makedirs(out_dir, exist_ok=True)
    for n, (title, buf) in enumerate(chapters, 1):
        fn = '%02d_%s.md' % (n, safe(title))
        with open(os.path.join(out_dir, fn), 'w', encoding='utf-8') as f:
            f.write('\n'.join(buf).rstrip() + '\n')
        print('  %-52s %5d 行' % (fn, len(buf)))
    print('%s：%d 个源文件 -> %s\n' % (src_md, len(chapters), out_dir))
    return len(chapters)


if __name__ == '__main__':
    books = BOOKS
    if '--book' in sys.argv:
        bk = sys.argv[sys.argv.index('--book') + 1]
        books = [b for b in BOOKS if b[1] == bk]
        if not books:
            print('未知 --book：%s（可选 dsdh / ar）' % bk)
            sys.exit(1)
    total = 0
    for md, key, repo in books:
        total += split(md, repo)
    print('合计 %d 个源文件。' % total)
