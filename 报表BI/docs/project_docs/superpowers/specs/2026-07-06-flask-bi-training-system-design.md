# Flask 商务智能实训系统设计规格

## 目标

围绕 `BIDemo_AccumulateCoin` 数据库完成“积分兑换平台 BI 系统”，按顺序交付三个独立项目：

1. `01_积分平台业务系统`
2. `02_金币联盟复刻系统`
3. `03_BI数据可视化大屏`

三个项目均使用 Flask、Jinja2、HTML、CSS、JavaScript 和 pyodbc。BI 大屏使用 ECharts。业务源库只使用 `BIDemo_AccumulateCoin`，数据仓库使用 `BI_GoldCoin_DW`。

## 已确认数据库状态

- SQL Server 默认实例可用，连接命令：`sqlcmd -S . -E -C`
- SQL Server 数据目录：`C:\Program Files\Microsoft SQL Server\MSSQL17.MSSQLSERVER\MSSQL\DATA`
- 当前核心表包括 `Account`、`AccountTradeIn`、`AccountTradeLog`、`AccountTradeOut`、`AreaInfo`、`BusinessMen`、`CityInfo`、`CustomerInfo`、`GiftInfo`、`JFCode`、`JFCode_import`、`OrderGift`、`OrderInfo`、`ProductInfo`、`ProvinceInfo`、`ZoneInfo`。
- 当前库已有大量会员、账户和流水，但商家、商品、礼品、订单不足；模拟数据脚本应按缺口补齐，不重置现有库。

## 核心业务规则

- `Account.Acctype=1` 表示会员账户，`Account.Acctype=2` 表示商家账户。
- `CustomerInfo` 是会员表，`BusinessMen` 是商家表，`ProductInfo` 归属 `BusinessMen`。
- `GiftInfo.GfitCoin` 是礼品兑换所需金币。
- `JFCode.JFCode1` 是明文积分码，`JFCode.JFCode` 是 MD5 后的码，`JFStatus=0/1/2` 表示无效、待使用、已使用。
- `CoinTrade @tradeType=2` 完成积金币。
- `AddOrder` 会扣礼品库存，并调用 `CoinTrade @tradeType=1` 完成兑换。

## 三项目边界

| 项目 | 职责 | 不做什么 |
|---|---|---|
| `01_积分平台业务系统` | 后台业务录入、积分、兑换、订单、流水、大数据生成 | 不复刻金币联盟、不做 BI 大屏 |
| `02_金币联盟复刻系统` | 面向会员的商城复刻、注册、登录、积金币、购物车、个人中心 | 不做后台管理、不做独立 BI 大屏 |
| `03_BI数据可视化大屏` | 数仓 SQL、ETL、Flask API、ECharts 单页大屏 | 不做商城操作、不做后台业务维护 |

## BI 主题和总线矩阵

BI 分析主题固定扩展为 9 个：

1. 商家统计分析
2. 会员统计分析
3. 礼品统计分析
4. 订单统计分析
5. 商家会员统计分析
6. 商品积分统计分析
7. 积分码使用统计分析
8. 积分流水统计分析
9. 地域统计分析

维度包括时间、小时、商家、商品、会员、礼品、积分码、积分方式、订单状态、地域。趋势使用折线图，排行使用柱状或条形图，占比使用环图，地域默认使用地域排行条形图。

## 验收标准

- 三个项目分属三个文件夹，并可独立运行。
- 每个项目包含 `DESIGN.md`。
- 业务系统能连接 `BIDemo_AccumulateCoin` 并完成核心业务流程。
- 金币联盟复刻系统使用原 ASP.NET 项目素材并复刻主要页面。
- BI 项目提供 8 个 SQL 脚本，能建立数据仓库、抽取数据并展示单页大屏。
