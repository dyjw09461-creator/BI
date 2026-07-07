# 积分兑换平台 BI 综合仪表盘实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 01 业务系统和 03 BI 大屏合并为一个可运行的积分兑换平台 BI 仪表盘。

**Architecture:** 01 Flask 项目作为主入口，业务页面保留，首页改为 BI 仪表盘。API 从 `BI_GoldCoin_DW` 的 Dashboard Views 取数，ECharts 负责图表展示。

**Tech Stack:** Flask, Jinja2, pyodbc, SQL Server, ECharts, HTML/CSS/JS。

## Global Constraints

- 业务源库只使用 `BIDemo_AccumulateCoin`。
- 数据仓库只使用 `BI_GoldCoin_DW`。
- 首页必须是单页 BI 仪表盘，不翻页。
- 图表必须匹配积分平台业务数据，不使用销售额、销售渠道、AdventureWorks 等无关字段。
- 地域数据若为区县级，使用排行条形图，不强行中国地图。

---

### Task 1: 合并 BI API

**Files:**
- Modify: `C:\Users\PXHONY\Desktop\BI\01_积分平台业务系统\config.py`
- Modify: `C:\Users\PXHONY\Desktop\BI\01_积分平台业务系统\app.py`
- Create: `C:\Users\PXHONY\Desktop\BI\01_积分平台业务系统\services\bi_service.py`

- [x] 增加 `DW_DATABASE` 配置。
- [x] 新增 `/api/bi/*` 接口。
- [x] 从 `BI_GoldCoin_DW` 的 Dashboard Views 读取 KPI、订单趋势、礼品排行、商家会员排行、积分码状态、地域排行、商品积分排行。

### Task 2: 重做首页仪表盘

**Files:**
- Modify: `C:\Users\PXHONY\Desktop\BI\01_积分平台业务系统\templates\dashboard.html`
- Create: `C:\Users\PXHONY\Desktop\BI\01_积分平台业务系统\static\css\bi_dashboard.css`
- Create: `C:\Users\PXHONY\Desktop\BI\01_积分平台业务系统\static\js\bi_dashboard.js`

- [x] 首页改为单页 BI 仪表盘。
- [x] 使用 `frontend-design` 的浅色科技驾驶舱视觉。
- [x] 接入 ECharts 图表。
- [x] 保留业务操作导航入口。

### Task 3: 验证

**Commands:**
- `python -m py_compile app.py services\bi_service.py services\business_service.py db\sqlserver.py`
- `node --check static\js\bi_dashboard.js`
- `Invoke-WebRequest http://127.0.0.1:5101/ -UseBasicParsing`
- 逐个请求 `/api/bi/*`。

- [x] 重启 5101。
- [x] 验证页面和 API。
- [x] 如可用，生成截图检查首屏视觉。
