## 模块四　文本挖掘与 NLP






> **学习目标**：完成本模块后，你应能（1）说明中文分词与句读的特殊性；（2）用分词 + TF-IDF/主题模型从语料中提炼结构；（3）用命名实体识别抽取人/地/时/事；（4）理解"历史语言"给 NLP 带来的适配难题，并能指出一处语料偏见。

### 4.1 文本是第一大类人文数据

![文本挖掘与主题模型概念图](assets/dsdh/Clean_academic_infographic_ill_2026-09-09T07-00-27.png)

模块二把文本列为五类之首，不是偶然——古籍、报刊、书信、剧本，构成了人文研究的主干材料。NLP 的任务，是把"人读得懂的字"变成"机器算得了的数"：词频、向量、实体、主题。

### 4.2 分词与预处理：中文的特殊性

英文靠空格分词，中文没有。通用工具（如 `jieba`）按现代语料训练，遇到**古籍异体字、避讳字、缺句读**就会翻车。预处理常做：

- **分词**：`jieba.lcut("关关雎鸠在河之洲")`；
- **去停用词**：去掉"之、乎、者、也"等高频无实义词；
- **句读还原**：古书无标点，需先补断句再分析。

> **提醒**：用现代分词器切古诗文，结果要人工抽查——"不亦说乎"被切成什么，决定了后续一切。

### 4.3 从词频到主题：词云、TF-IDF 与 LDA

- **词频/词云**：最快的"扫一眼重点"，但易被长文主导；
- **TF-IDF**：衡量"在这篇重要、在全集罕见"的词，比纯词频更准；
- **LDA 主题模型**：把成千上万篇自动归成若干"主题"，每篇是主题的混合。例如对近代报刊跑 LDA，可能析出"实业""教育""宪政"等隐主题。

### 4.4 命名实体识别：抽人、地、时、事

NER（命名实体识别）从文本里标出**人物、地点、时间、机构、事件**。对一部地方志跑 NER，能直接得到"某县出现过哪些名人、哪些水患、哪些书院"。这是后续网络分析（模块六）、空间分析（模块七）、知识图谱（模块九）的数据源头。

### 4.5 历史语言的麻烦：Adapting vs Pre-training

通用大模型在当代新闻上很强，在**历史语言**上常失灵——异体字、旧称、已消亡的语义。两条路（见本模块 V2.1 的 *Adapting vs. Pre-training Language Models for Historical Languages*、*Alien Reading*）：

- **Pre-training（从头训）**：用海量历史语料重训，最贴但最贵；
- **Adapting（适配）**：在通用模型上微调或加提示，成本可控，是人文项目的现实选择。

### 4.6 伦理坐标：语料偏见与"客观"幻象（本模块核心能力）

- **取样偏见**：能数字化的文本偏向"被保存下来的"——名家、官修、纸本，底层声音天然缺失；
- **词表偏见**：停用词表、主题数 k 都是人定的，k 取 5 还是 10，叙事就变；
- **"客观"幻象**：主题模型给的是统计结构，不是"历史真相"，别把机器聚类当定论。

> **一条红线**：不把 NLP 输出直接说成"古人就是这样想的"；呈现结果时同步交代语料与参数。

### 4.7 第一次动手：对一组诗文做主题模型

> **小练习 4.1（文本挖掘）**：取 10–50 篇同主题诗文（如某总集、某报刊专栏），用分词 + 去停用词 + TF-IDF 或 LDA 提炼 3–5 个主题，列出每主题的高权重词，并手判"这些词真的构成一个主题吗"。本模块 V2.2 的《数字人文视域下先秦典籍植物知识挖掘与组织研究》《基于 ChatGPT 和零样本提示的临床量表文本中结构化项目信息抽取研究》可作方法参照——前者是传统挖掘，后者是零样本提示抽取，对照看"老方法"与"新提示"的差异。


### 4.8 第二次动手：用 TF-IDF 对比两位作者
- **目标**：取两位诗人 / 作者的诗文各若干篇，用量化方法比较“谁更爱用某类词”。
- **步骤**：
  1. 各收集不少于 10 篇文本；
  2. 分词并去停用词；
  3. 用 TF-IDF 取各自 Top 20 关键词；
  4. 画两张词云或词频条形图；
  5. 写 150 字：差异能说明什么、不能说明什么。
- **工具**：jieba + sklearn `TfidfVectorizer`。
- **产出**：两张关键词图 + 一段解读。
- **评价量规**：分词去噪（30%）、TF-IDF 正确（30%）、解读克制（40%）。
### 4.9 本章小结

带走三件事：**中文预处理**（分词/停用词/句读）、**从词到主题**（TF-IDF/LDA）、**NER 抽实体**（人地时事）。记住 4.5 与 4.6：历史语言要适配，模型结论要带"语料与参数"的尾巴。

### 4.10 思考题

1. 用 `jieba` 切一句你专业的古文，结果哪里不对？这透露了现代分词器的什么盲区？
2. LDA 的"主题数 k"由人设定。k 取不同值，叙事会怎样变化？这算"主观"吗？
3. 如果一篇 NLP 论文声称"用主题模型发现了某思潮的兴起"，你会要求它补充哪些信息才敢引用？



### 4.11 思政融入（课程思政）

> **思政融入（课程思政）**：用 NLP 阐释古籍，是“守正创新”的生动实践：以新方法激活传统，但**必须以尊重原文与前人注疏为前提**，不以模型结论僭越历史。中华典籍是中华民族的智慧结晶，让技术使它“活起来”，正是增强**文化自信**的一条切实路径——前提是谦卑与严谨。

> **思政案例（课程思政示范案例 / AI 思政课 知识库）**：可参照《文化哲学》“坚持文化自信”与《中医基础理论》“中国传统文化”的育人切入点——以技术活化典籍，须以尊重传统为前提。


### 模块四·学术前沿：OpenAlex / DBLP / arXiv / CrossRef / CORE 实证文献（V2.1）

下表为通过 OpenAlex（开放学术图谱，聚合期刊/会议/预印本）、DBLP（CS 会议期刊，含 SIGIR/UIST/DH/IJDAR/EPIA）、arXiv（预印本）、CrossRef（期刊 DOI 元数据）、CORE（开放获取库）检索到的真实文献，按来源/被引排序，供延伸阅读与实验报告引用。

| 来源 | 年份 | 标题（链接） | 作者 / 场所 |
|------|------|--------------|----------------|
| CrossRef | 2022 | [Adapting vs. Pre-training Language Models for Historical Languages](https://doi.org/10.46298/jdmdh.9152) | Journal of Data Mining &amp; Digital Humanities（被引 27） |
| CrossRef | 2016 | [Alien Reading:](https://doi.org/10.5749/j.ctt1cn6thb.21) | Debates in the Digital Humanities 2016（被引 4） |
| CrossRef | 2024 | [NLP for Digital Humanities: Processing Chronological Text Corpora](https://doi.org/10.18653/v1/2024.nlp4dh-1.10) | Proceedings of the 4th International Conference on Natural Language Processing for Digital Humanities（被引 3） |
| CrossRef | 2024 | [Review for "Fine-tuning Large Language Models for Chemical Text Mining"](https://doi.org/10.1039/d4sc00924j/v1/review2) |  |
| CrossRef | 2026 | [Context-Enriched NLP Pipelines using Large Language Models for High Accuracy Text Mining and Sentiment Analysis](https://doi.org/10.1109/iccnct68477.2026.11590134) | 2026 International Conference on Computer Networks and Inventive Communication Technologies (ICCNCT) |
| CrossRef | 2026 | [Temporal Text Classification with Large Language Models](https://doi.org/10.18653/v1/2026.nlp4dh-1.10) | Proceedings of the 6th International Conference on Natural Language Processing for the Digital Humanities |
| CrossRef | 2024 | [Decision letter for "Fine-tuning Large Language Models for Chemical Text Mining"](https://doi.org/10.1039/d4sc00924j/v2/decision1) |  |
| CORE |  | [Natural language processing](https://core.ac.uk/download/9015693.pdf) | Chowdhury, Gobinda G., Chowdhury, G., Chowdhury, GG, Gobinda G. Chowdhury |

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

### 模块四·中文核心期刊文献实证（V2.2·19 种图情档核心期刊）

下表论文来自 19 种中文图情档核心期刊（中国图书馆学报、情报学报、情报资料工作、档案学通讯、大学图书馆学报、图书情报工作、数据分析与知识发现、情报杂志、情报理论与实践、图书与情报、档案学研究、图书馆杂志、图书情报知识、图书馆论坛、图书馆学研究、图书馆建设、情报科学、现代情报、信息资源管理学报），经 Web 检索（期刊官网 / CNKI 索引 / DOI 溯源）按主题核实得到真实文献（含 DOI/链接）。

| 来源期刊 | 年份 | 标题（链接） | 作者 |
|----------|------|--------------|------|
| 图书情报工作 | 2023 | [数字人文视域下先秦典籍植物知识挖掘与组织研究](https://doi.org/10.13266/j.issn.0252-3116.2023.12.010) | 吴梦成, 林立涛, 齐月, 黄水清, 王东波, 刘浏 |
| 图书情报工作 | 2024 | [基于ChatGPT和零样本提示的临床量表文本中结构化项目信息抽取研究](https://doi.org/10.13266/j.issn.0252-3116.2024.22.013) | 郝洁, 莫治强, 孙海霞, 陈振丽, 李姣 |
| 情报学报 | 2023 | [基于可解释图神经网络模型的社交媒体谣言识别研究](https://doi.org/10.3772/j.issn.1000-0135.2023.11.010) | 汪子航, 言鹏韦, 蒋卓人 |
| 情报学报 | 2024 | [基于知识增强的文本语义匹配模型研究](https://doi.org/10.3772/j.issn.1000-0135.2024.04.004) | 张贞港, 余传明 |

**课堂复现（中文文献检索）**：这些期刊正式全文多见于 CNKI/万方/维普（本环境无订阅）。可在机构网络以「期刊名 + 主题词」检索，导出 BibTeX/RIS 后交我并入；DOI 可在 https://doi.org/<DOI> 溯源摘要。

**误用警示**：① 引用以期刊正式版本为准（年/卷/期/页）；② 回到原文核对方法与数据；③ 与本节实验的映射是"启发"而非"背书"。

**与实验衔接**：将上表任一中文方法（如中文知识图谱、机器学习人文应用）对照本模块实验改写，即可形成有本土学术依据的结题报告。
