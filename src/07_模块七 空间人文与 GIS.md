## 模块七　空间人文与 GIS






> **学习目标**：完成本模块后，你应能（1）区分点、线、面三类空间数据；（2）说明"历史 GIS"为何要把时间叠在空间上；（3）用地理编码把一批地名变成坐标并落图；（4）指出地图本身可能承载的权力预设。

### 7.1 给人文加一个坐标

地点是人文材料的隐形骨架：地契的四至、游记的路线、人物的籍贯、事件的发生地。加上坐标，静态文本就活成可叠加、可计量的空间。

### 7.2 空间数据：点、线、面与格式

- **点**：一个坐标（某书院、某墓）；
- **线**：一连串坐标（驿道、河流、游记路线）；
- **面**：闭合区域（政区、田界、流域）；
- **格式**：`shapefile`、`GeoJSON` 是开放常用格式，pandas 读不了，要用 `geopandas`。

### 7.3 历史 GIS：时间 + 空间

今天的地图是"此刻"的。历史 GIS 要把**变迁**叠进去：同一块地，汉属某郡、唐属某道、今属某省。政区变了，坐标的含义也变（见本模块 V2.1 的 *Toward Spatial Humanities*、*GIS and Literary History*、*The Potential of Historical GIS and Spatial Analysis in the Humanities*）。所以空间人文的第一个难题，是"坐标系随时间漂移"。

### 7.4 空间分析：密度、邻近与扩散

- **密度**：某类遗址在哪些区域密集（如窑址分布）；
- **邻近**：事件是否围绕某中心聚集（如农民起义与粮仓距离）；
- **扩散**：技术/疫疾沿驿道如何传播。

这些问题的前提，是先有干净的坐标。

### 7.5 地理编码：把地名变成坐标

**地理编码（geocoding）** 把"杭州""汴京"映射到经纬度。难点在古今地名错位：用今图搜古名会落错点。CHGIS（中国历史地理信息系统）正是为解决这个问题而建——它给出历史政区的时空对应，是本课程推荐的时空数据源（模块二已列入开放门户表）。

### 7.6 伦理坐标：地图即权力（本模块核心能力）

- **投影即立场**：同一地球，不同投影夸大或缩小不同地区，默卡托投影曾服务于航海霸权；
- **边界即叙事**：画哪条界，就默认了哪方的主权；
- **被抹去的地点**：少数族群的栖居地、消失的村落，常在标准图上"不存在"。

> **一条红线**：不在地图上替争议领土/族群"做主"；标注坐标系与资料来源，让观者知道"这是哪一年的哪张图"。

### 7.7 第一次动手：把一批点位落图

> **小练习 7.1（空间人文）**：取 10–30 个你关心的地点（地契四至、游记经停、人物籍贯），查其古今坐标（可用 CHGIS / OpenStreetMap），用 `geopandas` 落在一张底图上，观察它们的聚集或迁移规律，并注明"坐标基于哪一年的政区"。


### 7.8 第二次动手：做一张“时间切片”历史地图
- **目标**：把同一批地名按不同朝代落图，看空间格局如何变化。
- **步骤**：
  1. 取一批带朝代字段的地名点位；
  2. 按朝代分组；
  3. 用不同颜色 / 图层画出 2–3 个时期；
  4. 标注每个时期的政治中心；
  5. 写 150 字：格局变化说明了什么。
- **工具**：QGIS 或 folium（Python）。
- **产出**：2–3 张时期地图 + 说明。
- **评价量规**：地理编码准确（30%）、分期合理（30%）、解读有据（40%）。
### 7.9 本章小结

带走三件事：**点线面 + 格式**（GeoJSON/shapefile）、**历史 GIS 的时间叠加**、**地理编码与批判**（投影/边界/被抹去）。坐标让人文"可叠加"，但坐标本身带着年代与立场。

### 7.10 思考题

1. 选一组古今同名的地名，它们在今天的地图与历史地图里位置一致吗？不一致会带来什么研究风险？
2. 地图的"投影"如何影响我们对"大小/远近"的感知？举一个你注意到的例子。
3. 如果一份史料里的地点今天已不存在于标准地图，你该如何诚实地呈现它？



### 7.11 思政融入（课程思政）

> **思政融入（课程思政）**：历史地理印证了**统一多民族国家**的形成与疆域变迁。在地图上呈现历代政区与疆界时，须以严谨史料为依据，捍卫国家领土完整的表述，不被错误边界误导。空间人文让我们“看见”祖国的辽阔与历史的纵深，这是**家国情怀**最具体的训练。

> **思政案例（课程思政示范案例 / AI 思政课 知识库）**：可参照《数字化测图》课程思政以无人机航测、GNSS 服务智慧城市与国家建设的案例——空间技术亦可报国，历史地理研究同样连着家国。


### 模块七·学术前沿：OpenAlex / DBLP / arXiv / CrossRef / CORE 实证文献（V2.1）

下表为通过 OpenAlex（开放学术图谱，聚合期刊/会议/预印本）、DBLP（CS 会议期刊，含 SIGIR/UIST/DH/IJDAR/EPIA）、arXiv（预印本）、CrossRef（期刊 DOI 元数据）、CORE（开放获取库）检索到的真实文献，按来源/被引排序，供延伸阅读与实验报告引用。

| 来源 | 年份 | 标题（链接） | 作者 / 场所 |
|------|------|--------------|----------------|
| CrossRef | 2014 | [Toward Spatial Humanities](https://doi.org/10.2979/6100.0) | （被引 45） |
| CrossRef | 2016 | [GIS and Literary History: Advancing Digital Humanities research through the Spatial Analysis of historical travel writing and topographical literature](https://doi.org/10.63744/j4zd5gkttdny) | Digital Humanities Quarterly（被引 3） |
| CrossRef | 2018 | [Spatial Humanities GIS: The City As a Literary, Historical, and Cultural STEAM Lifeworld Laboratory](https://doi.org/10.1007/978-3-319-89818-6_2) | The STEAM Revolution（被引 2） |
| CrossRef | 2014 | [Has Historical GIS Arrived?: A Review of Toward Spatial Humanities](https://doi.org/10.18737/m7k30v) | Southern Spaces（被引 1） |
| CrossRef | 2015 | [Toward spatial humanities: historical GIS &amp; spatial history](https://doi.org/10.1080/14649365.2015.1104884) | Social &amp; Cultural Geography（被引 1） |
| CrossRef | 2016 | [Toward Spatial Humanities: Historical GIS and Spatial History](https://doi.org/10.1016/j.jhg.2015.06.004) | Journal of Historical Geography |
| CrossRef | 2017 | [The Potential of Historical GIS and Spatial Analysis in the Humanities](https://doi.org/10.18737/m7jt3x) | Southern Spaces |
| CrossRef | 2025 | [Unearthing the Past: Finding Ancient Kannauj Through Remote Sensing and GIS](https://doi.org/10.1007/978-981-95-0117-5_6) | Spatial Narratives of India's Heritage: Integrating Geospatial Analysis in the Humanities |

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
