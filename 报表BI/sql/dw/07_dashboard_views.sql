USE BI_GoldCoin_DW;
GO

CREATE OR ALTER VIEW dbo.vw_dashboard_kpi AS
SELECT
    (SELECT COUNT(*) FROM dbo.Dim_Business) AS BusinessCount,
    (SELECT COUNT(*) FROM dbo.Dim_Customer) AS CustomerCount,
    (SELECT COUNT(*) FROM dbo.Dim_Gift) AS GiftCount,
    (SELECT COUNT(*) FROM dbo.Fact_Order) AS OrderCount,
    (SELECT ISNULL(SUM(CASE WHEN Coin>0 THEN Coin ELSE 0 END),0) FROM dbo.Fact_AccountTrade) AS CoinIn,
    (SELECT ISNULL(ABS(SUM(CASE WHEN Coin<0 THEN Coin ELSE 0 END)),0) FROM dbo.Fact_AccountTrade) AS CoinOut;
GO

CREATE OR ALTER VIEW dbo.vw_dashboard_order_trend AS
SELECT TOP 30 DateKey, COUNT(*) AS OrderCount, ISNULL(SUM(TotalCoin),0) AS TotalCoin
FROM dbo.Fact_Order
GROUP BY DateKey;
GO

CREATE OR ALTER VIEW dbo.vw_dashboard_member_trend AS
SELECT TOP 30 DateKey, COUNT(*) AS MemberCount
FROM dbo.Fact_Customer
GROUP BY DateKey;
GO

CREATE OR ALTER VIEW dbo.vw_dashboard_gift_ranking AS
SELECT g.GiftID, d.GiftName, ISNULL(g.ExchangeCount,0) AS ExchangeCount, ISNULL(g.ExchangeCoin,0) AS ExchangeCoin
FROM dbo.Fact_Gift g
LEFT JOIN dbo.Dim_Gift d ON d.GiftID=g.GiftID;
GO

CREATE OR ALTER VIEW dbo.vw_dashboard_business_member_ranking AS
SELECT b.BusinessID, d.BusinessCnName, COUNT(DISTINCT b.CustomerID) AS MemberCount, ISNULL(SUM(b.CoinContribution),0) AS CoinContribution
FROM dbo.Fact_BusinessCustomer b
LEFT JOIN dbo.Dim_Business d ON d.BusinessID=b.BusinessID
GROUP BY b.BusinessID,d.BusinessCnName;
GO

CREATE OR ALTER VIEW dbo.vw_dashboard_jfcode_status AS
SELECT JFStatus, COUNT(*) AS TotalCodes
FROM dbo.Fact_JFCode
GROUP BY JFStatus;
GO

CREATE OR ALTER VIEW dbo.vw_dashboard_area_ranking AS
SELECT a.AreaID, ISNULL(NULLIF(d.AreaName,N''),N'未知地域') AS AreaName, SUM(a.MemberCount) AS MemberCount, SUM(a.OrderCount) AS OrderCount, SUM(a.OrderCoin) AS OrderCoin
FROM dbo.Fact_AreaAnalysis a
LEFT JOIN dbo.Dim_Area d ON d.AreaID=a.AreaID
GROUP BY a.AreaID,d.AreaName;
GO

CREATE OR ALTER VIEW dbo.vw_dashboard_product_coin_ranking AS
SELECT p.ProductID, d.ProductName, p.CodeCount, p.UsedCodeCount, p.UsedCoin
FROM dbo.Fact_ProductCoin p
LEFT JOIN dbo.Dim_Product d ON d.ProductID=p.ProductID;
GO
