# Flask 商务智能实训系统实施计划

## Summary

基于现有规格、Word 提取内容、ASP.NET 金币联盟页面和当前 SQL Server 库结构，按三个独立 Flask 项目交付：

1. `C:\Users\PXHONY\Desktop\BI\01_积分平台业务系统`
2. `C:\Users\PXHONY\Desktop\BI\02_金币联盟复刻系统`
3. `C:\Users\PXHONY\Desktop\BI\03_BI数据可视化大屏`

执行顺序固定为业务系统、金币联盟复刻、BI 大屏。每个前端项目先生成 `DESIGN.md`，再按该设计实现代码。

## Key Changes

- 三个项目都使用 `Flask + Jinja2 + HTML/CSS/JS + pyodbc`，BI 项目额外使用 `ECharts`。
- 数据库连接统一使用 Windows 集成认证：`DRIVER={ODBC Driver 18 for SQL Server};SERVER=.;Trusted_Connection=yes;TrustServerCertificate=yes`。
- 业务源库只使用 `BIDemo_AccumulateCoin`；数据仓库只创建 `BI_GoldCoin_DW`。
- 不重置现有业务库；数据生成脚本按缺口补齐目标规模。
- 业务系统新增支持 SQL 脚本，补齐注册、商品、礼品、积分码批量生成过程；积分获取调用 `CoinTrade @tradeType=2`，礼品兑换调用 `AddOrder`。

## Implementation Plan

### Phase 0: 计划和设计文件

- 保存本计划到 `docs\superpowers\plans\2026-07-06-flask-bi-training-system-plan.md`。
- 优化规格文件，补入数据库状态、存储过程参数、9 个 BI 主题、总线矩阵扩展和三项目边界。
- 为三个项目分别生成 `DESIGN.md`。

### Phase 1: 积分平台业务系统

- 创建独立 Flask 项目结构。
- 实现会员、商家、商品、礼品、积分码、积分获取、礼品兑换、订单、流水和数据生成。
- 页面按后台业务系统实现，首页是管理仪表盘。

### Phase 2: 金币联盟复刻系统

- 创建独立 Flask 项目结构。
- 复制原金币联盟素材并复刻 8 个页面路由。
- 注册、登录、积金币、购物车、个人中心接业务库。

### Phase 3: BI 数据可视化大屏

- 创建独立 Flask + SQL 项目。
- 提供 `01_create_dw_database.sql` 到 `08_seed_large_business_data.sql`。
- 实现 9 个 BI 分析主题和单页 ECharts 大屏。

## Test Plan

- `sqlcmd -S . -E -C -d BIDemo_AccumulateCoin -Q "SELECT COUNT(*) FROM CustomerInfo"`
- 每个 Flask 项目运行 `python -m py_compile app.py config.py db\sqlserver.py services\*.py`。
- 业务系统访问主要路由并验证 SQL 查询可执行。
- 金币联盟访问 8 个路由并验证素材存在。
- BI 大屏执行 SQL 文件语法检查和 API 结构检查。

## Assumptions

- 不删除、不重置现有业务数据。
- 密码按实训用途保留简单字段写入。
- `JFCode.JFStatus` 采用 `0` 无效、`1` 待使用、`2` 已使用。
- 地域图默认用横向条形图，避免本地地图数据依赖。
