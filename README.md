# 《数据科学与数字人文》互动教材

**在线地址**：<https://sghpedc5279.github.io/dsdh/>

苏州大学社会学院 · 图情档方向课程教材，含 **12 个模块 + 综合项目**。

## 站点结构

| 文件 | 说明 |
|---|---|
| `index.html` | 首页，提供「在线阅读」与「章节下载」两个入口 |
| `book.html` | 互动翻页教材，171 页，16:9 显示，单文件离线可用 |
| `download.html` | 章节 Word 文档下载页 |
| `chapters/` | 14 篇按模块拆分的 docx（图片已内嵌） |
| `.github/workflows/deploy-pages.yml` | GitHub Actions 自动部署配置 |

## 阅读操作

- 键盘 `←` `→` 翻页 · `T` 打开目录 · `F` 全屏
- 点击任意图片可全屏查看（灯箱），`Esc` 关闭

## 课堂互动

教材已按章节拆分为 14 篇 docx，可**批量导入飞书知识库**（导入为在线文档 → Microsoft Word），
学生即可在文档中使用「划词评论」参与课堂讨论与提问。

## 更新内容

教材正文维护在 `数据科学与数字人文_教材编写.md`。改完后：

```bash
cd "C:\Users\sghpe\Desktop\BaiduSyncdisk\两本教材"

# 1. 重新生成翻页教材（用普通 Python 即可）
python build_flipbook.py
cp "数据科学与数字人文_互动翻页教材.html" dsdh-pages/book.html

# 2. 重新拆分章节 docx（须用隔离 venv 解释器，它才带 python-docx）
C:/Users/sghpe/.workbuddy/binaries/python/envs/default/Scripts/python.exe split_for_feishu.py
cp "飞书导入/DSDH/"*.docx dsdh-pages/chapters/

# 3. 提交并推送，GitHub Actions 自动部署
git -C dsdh-pages add -A
git -C dsdh-pages commit -m "更新教材内容"
git -C dsdh-pages push
```

## 部署方式

GitHub Actions 自动部署，推送到 `main` 分支即触发。

> 首次部署需在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**（一次性人工操作）。
