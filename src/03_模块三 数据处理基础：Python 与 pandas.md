## 模块三　数据处理基础：Python 与 pandas






> **学习目标**：完成本模块后，你应能（1）在统一预部署环境中运行第一段 Python 并读懂报错；（2）用 pandas 读入、筛选、分组聚合一份 CSV；（3）理解"可复现流水线"的含义——随机种子、版本、环境皆可见；（4）独立完成第一次数据清洗：处理缺失、重复与类型错误。

### 3.1 为什么要学一点 Python：不是要你当程序员

本书承诺"可复现"，而可复现的底线是**把操作变成代码**。你不必成为算法工程师，但值得亲手写出第一条流水线：别人能重跑你的步骤，得到一样的结果。Python 是这门课的统一语言，因为它免费、生态成熟、中文社区友好。

### 3.2 十分钟上手：变量、列表、字典与函数

只需要四个概念就能开工：

- **变量**：`n = 1949` 把"年份"存起来；
- **列表**：`years = [1949, 1989, 2024]` 装一组值；
- **字典**：`record = {"name": "Busa", "year": 1949}` 用"键"取"值"；
- **函数**：`def count(items): ...` 把重复操作打包复用。

记住：Python 对缩进敏感，层级靠空格表达，这点和写大纲一样自然。

### 3.3 pandas 三件套：Series、DataFrame 与读写

`pandas` 是数据科学的"表格引擎"。两类核心对象：

- **Series**：一列带索引的值（如某朝代所有诗人的生年）；
- **DataFrame**：多列组成的表（如"诗人—生年—籍贯—作品数"）。

读写一行就够：`df = pd.read_csv("poets.csv")`、`df.to_csv("clean.csv", index=False)`。本环境已预装 pandas，导入即用的代码不依赖外网。

### 3.4 数据清洗四板斧

真实人文数据几乎没有"干净的"。常做的四件事：

- **缺失**：`df.dropna()` 丢空行，或 `df.fillna(0)` 补默认值；
- **重复**：`df.drop_duplicates()` 去重（同一首诗被不同库收录两次很常见）；
- **类型**：`df["year"] = df["year"].astype(int)` 把"字符型年份"变成能算的数；
- **重命名**：`df.rename(columns={"籍貫":"籍贯"})` 统一字段名，避免后续对不上。

> **经验**：清洗不是"美化"，而是"留痕"。每步改动都写进脚本，别人才能复现你的取舍。

### 3.5 分组与聚合：groupby 的人文用法

`groupby` 是提问的利器。例如"统计每个朝代各有多少位诗人"：

```python
import pandas as pd
df = pd.read_csv("poets.csv")
print(df.groupby("dynasty")["name"].count())
```

一句话，就把"感觉宋代诗人多"变成了"数出来宋代 312 位、唐代 228 位"。本模块 V2.1 文献中的 *Data Wrangling using Pandas*、*Chapter 3: Introduction to Pandas*、*Chapter 6: Data Cleaning Tasks* 是系统参照。

### 3.6 伦理坐标：可复现即学术诚信（本模块核心能力）

- **随机种子**：凡有随机（抽样、拆分），先 `random.seed(42)`，否则别人跑不出你的结果；
- **版本留痕**：记下 pandas / Python 版本，依赖变了行为可能变；
- **环境一致**：统一预部署环境，避免"在我电脑上是好的"；
- **不篡改**：清洗可以丢弃异常值，但必须说明为何丢弃，而非悄悄抹掉。

> **一条红线**：为"让结论好看"而删改数据，是比代码写错更严重的失信。

> **现实案例 3.1（2026 年"学术打假"风暴：数据造假的统计指纹）**
>
> 2026 年 4 月起，一位科普博主连续发布视频，质疑多位知名学者发表在《自然》(Nature) 及其子刊上的论文存在数据造假。其方法本质就是**数据审计**：下载论文补充材料，逐一检查原始数值的分布是否符合真实实验应有的随机性。被指出的典型"统计指纹"有三类——
> - **过度规律**：多组测量值之间呈现固定的绝对差值（有研究者估算，此类规律自然发生的概率低至 10⁻²³ 量级）；
> - **末位偏态**：数千个数值中，某一末位数字的出现频率是其他数字的十几倍；
> - **整列复制**：一列数据复制后统一加上一个小增量，形成"看起来像实验、实为填表"的伪数据。
>
> 后续进展均出自官方通报，可逐条溯源：2026 年 5 月，涉事高校通报认定该 Nature 论文存在学术不端，通讯作者被免去行政职务并降级，第一作者被解除聘用关系；7 月 30 日，Nature 正式撤稿，同日《自然-癌症》撤回另一篇涉事论文，《自然-细胞生物学》发布更正声明；8 月，国家自然科学基金委员会通报的科研不端案件中，有 4 起回应了此次网络举报，撤销项目并追回资金。同期《科学》(Science) 也就另一篇论文发布了"编辑关注声明"。
>
> **与本课程的关系**：把这些造假数据交给模块二学的"数据审计"三步法、本模块的"清洗四板斧"，几乎一眼可辨。可复现从来不只是技术要求——它是让造假无法藏身的最低门槛。
>
> **但请同时记住另一面**：Nature 系列期刊在回应中强调，所有相关案例仅占 2020 年以来中国作者在其原创研究期刊所发表论文的 **0.06%**。问题的严重性在于影响与后果，而不在比例；既不能讳疾忌医，也不能以偏概全地否定整个学术共同体。
>
> *资料来源：Nature 撤稿声明（2026-07-30）；涉事高校调查通报（2026-05）；国家自然科学基金委员会科研不端案件通报（2026-08-28）；Science 编辑关注声明（2026-07-30）。*

### 3.7 第一次动手：用真实数据做 EDA

> **小练习 3.1（可复现清洗）**：取模块二小练习里你审计过的数据集（或任意一份 CSV），在预部署环境用 pandas 完成：① 读入并 `.info()` 看字段与缺失；② 处理缺失/重复；③ 用一个 `groupby` 回答一个真问题（如"按年份统计文献数量"）；④ 把清洗后结果存为新 CSV，并在报告里写明每一步。这就是"采集→清洗"这一段的第一次落地。


### 3.8 第二次动手：用 groupby 复现一张论文统计表
- **目标**：找一篇用了“按年份 / 类别分组计数”的人文论文，用 pandas 复现它的分组表。
- **步骤**：
  1. 取一份带类别字段的数据集；
  2. 用 `df.groupby([...]).agg(...)` 得到计数；
  3. 与原表逐格核对；
  4. 若对不上，定位是口径差异还是数据差异；
  5. 输出核对结果。
- **工具**：pandas。
- **产出**：复现的分组表 + 核对说明。
- **评价量规**：groupby 正确（40%）、核对有据（40%）、解释清晰（20%）。
### 3.9 本章小结

带走三件事：**pandas 三件套**（Series/DataFrame/读写）、**清洗四板斧**（缺失/重复/类型/重命名）、**可复现纪律**（种子/版本/环境/留痕）。模块一说的流水线"采集→清洗→建模→验证→沟通"，你今天走完了前两步。

### 3.10 思考题

1. 找一份你专业里的 Excel/CSV 数据，用 3.4 的四板斧检查它有哪些"不干净"的地方？
2. "可复现"在人文研究中为何比在实验中更难？举一个你领域的例子。
3. 如果清洗时必须丢弃一批异常记录，怎样做才既诚实又不误导？



### 3.11 思政融入（课程思政）

> **思政融入（课程思政）**：“可复现”看似技术习惯，实则关乎**学术诚信与工匠精神**。每一次如实记录、每一份可重跑的代码，都是对真理的尊重，也是对后学的负责。诚信是科研底线，也是立德树人的根本——从第一行代码起，就把“求真、求实”刻进习惯。

> **思政案例（课程思政示范案例 / AI 思政课 知识库）**：可参照《会计学》课程思政“人无信不立，业无信不兴”的职业道德与法律意识——可复现、如实记录，正是学术诚信的底线训练。


### 模块三·学术前沿：OpenAlex / DBLP / arXiv / CrossRef / CORE 实证文献（V2.1）

下表为通过 OpenAlex（开放学术图谱，聚合期刊/会议/预印本）、DBLP（CS 会议期刊，含 SIGIR/UIST/DH/IJDAR/EPIA）、arXiv（预印本）、CrossRef（期刊 DOI 元数据）、CORE（开放获取库）检索到的真实文献，按来源/被引排序，供延伸阅读与实验报告引用。

| 来源 | 年份 | 标题（链接） | 作者 / 场所 |
|------|------|--------------|----------------|
| CrossRef | 2024 | [Data Wrangling using Pandas](https://doi.org/10.1007/979-8-8688-0602-5_2) | Data Engineering for Machine Learning Pipelines（被引 1） |
| CrossRef | 2022 | [Chapter 1: Introduction to Python](https://doi.org/10.1515/9781683929031-002) | Data Wrangling Using Pandas, SQL, and Java |
| CrossRef | 2022 | [Chapter 7: Data Wrangling](https://doi.org/10.1515/9781683929031-008) | Data Wrangling Using Pandas, SQL, and Java |
| CrossRef | 2023 | [Data wrangling with Python](https://doi.org/10.1007/978-981-19-7702-2_4) | Python Data Science |
| CrossRef | 2022 | [Chapter 3: Introduction to Pandas](https://doi.org/10.1515/9781683929031-004) | Data Wrangling Using Pandas, SQL, and Java |
| CrossRef | 2022 | [Chapter 6: Data Cleaning Tasks](https://doi.org/10.1515/9781683929031-007) | Data Wrangling Using Pandas, SQL, and Java |
| CrossRef | 2022 | [Preface](https://doi.org/10.1515/9781683929031-001) | Data Wrangling Using Pandas, SQL, and Java |
| CrossRef | 2026 | [28 Data Visualization with Pandas](https://doi.org/10.3139/9781569909607.028) | Numeric Python |

**课堂复现（检索即方法）**：下列代码直接调用 OpenAlex 免费 API 复现本模块文献检索（无需密钥）。

```python
import urllib.request, urllib.parse, json
q = 'data science digital humanities'
url = 'https://api.openalex.org/works?search=' + urllib.parse.quote(q) + '&per_page=10&sort=cited_by_count:desc'
oa = json.loads(urllib.request.urlopen(url, timeout=30).read())
for w in oa['results']:
    print(w['publication_year'], w['title'], '->', (w.get('primary_location') or {}).get('source', {}).get('display_name'))
```

**误用警示**：① arXiv 预印本未经同行评审，引用须标 preprint 并追正式版；② 被引数代表影响力非结论正确；③ 商业库（WoS/Scopus/Elsevier/JSTOR/CNKI）本环境无订阅，需机构账号获取后再并入。

**与实验衔接**：将任一方法对照本模块实验改写数据集或提示词，即可形成有学术依据的结题报告。
