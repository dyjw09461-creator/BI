# 报表BI 项目说明文档

这个项目是我在“积分兑换平台 BI 系统”实训里整理出来的最终报表项目。最开始我的理解是只做几个普通报表就可以，但是看完实训要求以后，我觉得应该先把业务系统的数据关系理清楚，再根据业务主题搭建数据仓库，最后用一个数据可视化大屏把结果展示出来，所以这个项目里面同时包含了业务数据维护、数据仓库 SQL、ETL 脚本和 BI 仪表盘。

项目的数据源使用的是 `BIDemo_AccumulateCoin`，数据仓库单独建成 `BI_GoldCoin_DW`。前端展示没有使用传统 SSRS 报表，而是用 `Flask + HTML + ECharts` 做成单页数据可视化大屏，这样展示效果更直观，也更适合商家、会员、礼品、订单这些主题的统计分析。

## 一、项目目标

本项目主要完成积分兑换平台的 BI 核心功能，重点不是单纯把数据库表查出来，而是按照业务分析的思路，把数据从业务库整理到数仓，再通过报表页面展示出来。

我给这个项目定的目标主要有这些：

1. 实现商家统计分析，查看商家数量、商家会员贡献和商品积分贡献。
2. 实现会员统计分析，查看会员规模、会员增长和地域分布。
3. 实现礼品统计分析，查看礼品库存、兑换次数和兑换金币。
4. 实现订单统计分析，查看订单趋势、订单积分和订单状态。
5. 实现积分码分析，统计积分码待使用、已使用和无效状态。
6. 实现积分流水分析，统计金币收入、金币支出和账户交易情况。
7. 根据业务系统设计数据仓库模型，包括 ODS、维度表、事实表和 Dashboard 视图。
8. 编写全量 ETL 和增量 ETL 脚本，让业务库数据可以抽取到数据仓库。
9. 使用 ECharts 做一个不翻页的 BI 大屏，把不同主题用合适的图表展示出来。

## 二、我对业务的理解

这个平台的核心业务其实是“积分获取”和“积分兑换”。

会员通过商品上的积分码获取金币，积分码对应商品，商品又属于商家，所以积分获取这条线可以分析出商家贡献、商品贡献、积分码使用情况。会员拿到金币以后，可以兑换平台礼品，兑换时会生成订单和订单明细，所以兑换这条线可以分析出礼品热度、订单趋势、积分消耗情况。

所以我把业务拆成了几条主线：

| 业务主线 | 涉及内容 | 后续分析方向 |
|---|---|---|
| 会员注册 | 会员、会员账户、地域 | 会员数量、增长趋势、地域分布 |
| 商家入驻 | 商家、商家账户、商品 | 商家数量、商品数量、贡献排行 |
| 积分码发放 | 商品、积分码、批次、状态 | 积分码使用率、商品积分贡献 |
| 积分获取 | 会员账户、商家账户、交易流水 | 金币收入、商家会员贡献 |
| 礼品兑换 | 礼品、库存、订单、订单明细 | 礼品排行、订单趋势、金币消耗 |
| 地域分析 | 省市区、会员、订单 | 区域会员和订单分布 |

这样设计以后，BI 报表不是孤立的页面，而是和业务流程对应起来的。

## 三、整体设计思路

我这个项目是按下面的顺序做的：

```text
先理解业务库 BIDemo_AccumulateCoin
        ↓
整理业务主题和总线矩阵
        ↓
设计数据仓库 BI_GoldCoin_DW
        ↓
编写 ODS、维表、事实表 SQL
        ↓
编写全量 ETL 和增量 ETL
        ↓
创建 Dashboard 统计视图
        ↓
用 Flask 提供 BI API
        ↓
用 ECharts 做单页可视化大屏
```

这样做的好处是每一步都有对应产物。业务库负责原始业务数据，数据仓库负责清洗和汇总，Flask 负责查询接口和页面路由，ECharts 负责最后展示。

## 四、总线矩阵设计

在原来实训给出的总线矩阵基础上，我这里把主题扩展得更多一些，因为只做商家、会员、礼品、订单四个主题会有点单薄。最后我在项目里覆盖了下面这些分析主题：

| 分析主题 | 时间维度 | 商家维度 | 会员维度 | 商品维度 | 礼品维度 | 积分码维度 | 地域维度 | 订单状态维度 |
|---|---|---|---|---|---|---|---|---|
| 商家统计分析 | √ | √ |  | √ |  |  |  |  |
| 会员统计分析 | √ |  | √ |  |  |  | √ |  |
| 礼品统计分析 |  |  |  |  | √ |  |  |  |
| 订单统计分析 | √ |  | √ |  | √ |  | √ | √ |
| 商家会员统计分析 | √ | √ | √ |  |  |  |  |  |
| 商品积分统计分析 | √ | √ |  | √ |  | √ |  |  |
| 积分码使用统计分析 | √ |  |  | √ |  | √ |  |  |
| 积分流水统计分析 | √ | √ | √ | √ |  | √ |  |  |
| 地域统计分析 | √ |  | √ |  |  |  | √ |  |

我这样扩展之后，报表页面里的图表就不只是几个简单柱状图，而是可以覆盖商家、会员、商品、礼品、订单、积分码、流水、地域这些完整的业务分析方向。

## 五、数据仓库模型设计

数据仓库名称为：

```text
BI_GoldCoin_DW
```

我的设计是分三层：

1. ODS 层：基本复制业务库中的核心业务表，保留原始数据结构，方便后面追溯。
2. 维度层：把分析时经常使用的对象抽出来，比如时间、商家、会员、商品、礼品、地域等。
3. 事实层：围绕业务过程建事实表，比如订单事实、积分流水事实、礼品兑换事实、商品积分事实等。

### 5.1 维度表

项目中设计的维度表如下：

| 维度表 | 说明 |
|---|---|
| `Dim_Date` | 日期维度，用来支持按日、月、季度、年分析 |
| `Dim_Hour` | 小时维度，用来支持订单和流水的时段分析 |
| `Dim_Business` | 商家维度 |
| `Dim_Product` | 商品维度 |
| `Dim_Customer` | 会员维度 |
| `Dim_Gift` | 礼品维度 |
| `Dim_Area` | 地域维度 |
| `Dim_JFCode` | 积分码维度 |
| `Dim_TradeType` | 交易类型维度 |
| `Dim_OrderStatus` | 订单状态维度 |

### 5.2 事实表

项目中设计的事实表如下：

| 事实表 | 说明 |
|---|---|
| `Fact_Business` | 商家统计事实，统计商家数量、启用商家、商品数量 |
| `Fact_Customer` | 会员统计事实，统计会员、地域和账户金币 |
| `Fact_Gift` | 礼品事实，统计库存、兑换次数、兑换金币 |
| `Fact_Order` | 订单事实，统计订单、订单时间、订单状态和总金币 |
| `Fact_BusinessCustomer` | 商家会员事实，统计商家带来的会员和积分贡献 |
| `Fact_ProductCoin` | 商品积分事实，统计商品积分码和已使用积分 |
| `Fact_JFCode` | 积分码事实，统计积分码状态 |
| `Fact_AccountTrade` | 积分流水事实，统计金币收入和支出 |
| `Fact_AreaAnalysis` | 地域分析事实，统计地域会员数、订单数、订单金币 |

## 六、ETL 设计

ETL 脚本分为全量抽取和增量抽取。

全量抽取主要用于第一次初始化数据仓库，会清理旧数据后重新从业务库抽取。增量抽取主要用于后续更新，只同步业务库中新产生或变化的数据。

ETL 的基本逻辑是：

```text
从 BIDemo_AccumulateCoin 抽取业务表
        ↓
写入 BI_GoldCoin_DW 的 ODS 表
        ↓
从 ODS 加工维度表
        ↓
从 ODS 和维度表加工事实表
        ↓
生成 Dashboard Views 给前端查询
```

本项目中的 ETL 脚本在：

```text
sql/dw/05_full_etl.sql
sql/dw/06_incremental_etl.sql
```

## 七、报表大屏设计

报表页面使用 Flask 渲染基础 HTML，然后通过 JavaScript 请求后端 API，再用 ECharts 画图。这样做的原因是 ECharts 对仪表盘、趋势图、极坐标、矩形树图这些图表支持比较好，比普通表格展示更直观。

大屏页面是单页展示，不做翻页，主要分成这些区域：

| 区域 | 展示内容 | 图表类型 |
|---|---|---|
| 顶部 KPI | 商家数、会员数、礼品数、订单数、金币收入、金币支出 | 数字指标卡 |
| 订单趋势 | 订单数量和兑换积分变化 | 折线图 / 面积图 |
| 总线矩阵覆盖 | 当前 BI 主题覆盖情况 | 矩阵卡片 |
| 积分码状态 | 待使用、已使用、无效 | 环图 |
| 商品积分贡献 | 商品积分码贡献结构 | 矩形树图 |
| 商家会员贡献 | 商家会员规模对比 | 极坐标图 |
| 礼品兑换分析 | 礼品兑换次数和客单积分 | 柱状图 + 折线图 |
| 地域分布 | 区域会员和订单分布 | 排行/地图区域 |
| 业务观察 | 根据当前统计结果生成提示 | 文本观察卡 |

我选择这些图表时，主要考虑的是数据适配性：趋势类数据用折线图，排行类数据用柱状图，结构占比用环图，商品贡献用矩形树图，商家规模对比用极坐标图。

## 八、项目目录说明

```text
报表BI/
├─ app.py                         Flask 路由入口，负责页面和 API
├─ config.py                      SQL Server 连接配置
├─ requirements.txt               Python 依赖
├─ DESIGN.md                      前端设计规范
├─ README.md                      当前项目说明文档
├─ db/
│  └─ sqlserver.py                pyodbc 数据库访问封装
├─ services/
│  ├─ business_service.py         业务库管理功能，如会员、商家、商品、礼品、积分码、订单、流水
│  └─ bi_service.py               BI 查询服务，读取数据仓库 Dashboard 视图
├─ templates/
│  ├─ dashboard.html              BI 大屏页面
│  ├─ base.html                   后台管理基础模板
│  ├─ list.html                   通用列表页模板
│  ├─ action.html                 积分获取、礼品兑换操作页
│  └─ seed.html                   数据准备说明页
├─ static/
│  ├─ css/app.css                 后台管理页面样式
│  ├─ css/bi_dashboard.css        BI 大屏样式
│  └─ js/bi_dashboard.js          ECharts 图表渲染逻辑
├─ sql/
│  ├─ 01_business_support_procs.sql       业务库支持脚本
│  ├─ 02_seed_large_business_data.sql     业务库大数据量造数脚本
│  └─ dw/
│     ├─ 01_create_dw_database.sql        创建数据仓库
│     ├─ 02_create_ods_tables.sql         创建 ODS 表
│     ├─ 03_create_dim_tables.sql         创建维度表
│     ├─ 04_create_fact_tables.sql        创建事实表
│     ├─ 05_full_etl.sql                  全量 ETL
│     ├─ 06_incremental_etl.sql           增量 ETL
│     ├─ 07_dashboard_views.sql           BI 大屏统计视图
│     └─ 08_seed_large_business_data.sql  数据仓库配套说明脚本
└─ docs/project_docs/             项目设计规格和实施计划
```

## 九、运行环境

我本机使用的环境是：

| 环境 | 说明 |
|---|---|
| Python | Python 3.10 |
| Web 框架 | Flask |
| 数据库 | SQL Server |
| 数据库连接 | pyodbc |
| 前端图表 | ECharts |
| 业务库 | `BIDemo_AccumulateCoin` |
| 数据仓库 | `BI_GoldCoin_DW` |

SQL Server 本机连接使用 Windows 身份验证。因为本机 ODBC Driver 18 默认会校验证书，所以执行 `sqlcmd` 时需要加 `-C`。

## 十、SQL 执行步骤

### 10.1 先处理业务库支持脚本

先进入项目目录：

```powershell
cd C:\Users\PXHONY\Desktop\BI\报表BI
```

执行业务库支持脚本：

```powershell
sqlcmd -S . -E -C -d BIDemo_AccumulateCoin -i sql\01_business_support_procs.sql
```

如果需要补充较大的测试数据，再执行：

```powershell
sqlcmd -S . -E -C -d BIDemo_AccumulateCoin -i sql\02_seed_large_business_data.sql
```

### 10.2 创建数据仓库

数据仓库脚本需要按文件名前缀顺序执行：

```powershell
sqlcmd -S . -E -C -i sql\dw\01_create_dw_database.sql
sqlcmd -S . -E -C -d BI_GoldCoin_DW -i sql\dw\02_create_ods_tables.sql
sqlcmd -S . -E -C -d BI_GoldCoin_DW -i sql\dw\03_create_dim_tables.sql
sqlcmd -S . -E -C -d BI_GoldCoin_DW -i sql\dw\04_create_fact_tables.sql
sqlcmd -S . -E -C -d BI_GoldCoin_DW -i sql\dw\05_full_etl.sql
sqlcmd -S . -E -C -d BI_GoldCoin_DW -i sql\dw\07_dashboard_views.sql
```

后续如果业务库又新增了数据，可以执行增量 ETL：

```powershell
sqlcmd -S . -E -C -d BI_GoldCoin_DW -i sql\dw\06_incremental_etl.sql
```

## 十一、启动项目

安装依赖：

```powershell
cd C:\Users\PXHONY\Desktop\BI\报表BI
pip install -r requirements.txt
```

启动 Flask：

```powershell
python app.py
```

如果要使用我本机这个 Python 路径，也可以这样启动：

```powershell
& 'C:\Users\PXHONY\AppData\Local\Programs\Python\Python310\python.exe' app.py
```

启动后访问：

```text
http://127.0.0.1:5101
```

首页就是 BI 仪表盘。页面上方导航可以进入会员、商家、商品、礼品、积分码、订单、积分流水等后台管理模块。

## 十二、后端接口设计

BI 大屏的数据接口都在 `app.py` 里，实际查询逻辑在 `services/bi_service.py` 中。接口对应关系如下：

| 接口 | 用途 |
|---|---|
| `/api/bi/kpi` | 顶部 KPI 指标 |
| `/api/bi/order-trend` | 订单和积分趋势 |
| `/api/bi/member-trend` | 会员增长趋势 |
| `/api/bi/gift-ranking` | 礼品兑换排行 |
| `/api/bi/business-member-ranking` | 商家会员贡献排行 |
| `/api/bi/jfcode-status` | 积分码状态统计 |
| `/api/bi/area-ranking` | 地域会员和订单排行 |
| `/api/bi/product-coin-ranking` | 商品积分贡献排行 |

后台管理页面也放在同一个 Flask 项目里，主要是为了方便实训演示时从业务数据维护到 BI 展示形成闭环。

## 十三、当前项目完成情况

目前这个项目已经完成：

1. Flask 项目基础结构。
2. SQL Server 连接封装。
3. 会员、商家、商品、礼品、积分码、订单、流水等后台页面。
4. 积分获取和礼品兑换操作页面。
5. 数据仓库建库脚本。
6. ODS、维度表、事实表脚本。
7. 全量 ETL 和增量 ETL 脚本。
8. Dashboard Views 统计视图。
9. ECharts 单页 BI 仪表盘。
10. 前端设计规范 `DESIGN.md`。

## 十四、我设计这个项目时的考虑

我没有一开始就直接画报表，而是先从业务表关系入手。因为如果业务逻辑没有理清楚，后面的报表很容易变成简单查表，体现不出 BI 的意义。

我把业务库看成原始系统，把 `BI_GoldCoin_DW` 看成分析系统。业务库里保存的是会员、商家、商品、积分码、订单和流水这些明细数据；数据仓库里则把这些数据重新整理成维度和事实，方便按主题分析。

前端没有做成很多分页报表，而是集中成一个大屏。这样做主要是为了展示效果更好，也能把“商家统计、会员统计、礼品统计、订单统计”这些要求放在同一张页面里对比查看。

整体来说，这个项目的思路就是：

```text
业务数据真实存在
数仓模型能解释业务
ETL 能把数据抽取过去
报表页面能把分析结果展示出来
```

这样最后提交的时候，既能说明模型设计，也能演示系统运行效果。
