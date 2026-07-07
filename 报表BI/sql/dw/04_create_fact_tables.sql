USE BI_GoldCoin_DW;
GO

DROP TABLE IF EXISTS dbo.Fact_Business,dbo.Fact_Customer,dbo.Fact_Gift,dbo.Fact_Order,dbo.Fact_BusinessCustomer,dbo.Fact_ProductCoin,dbo.Fact_JFCode,dbo.Fact_AccountTrade,dbo.Fact_AreaAnalysis;
GO

CREATE TABLE dbo.Fact_Business(BusinessID int, DateKey int, BusinessCount int, EnabledBusinessCount int, DisabledBusinessCount int, ProductCount int, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Fact_Customer(CustomerID int, DateKey int, AreaID int NULL, FromBusiness int NULL, CustomerCount int, ValidCoin bigint, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Fact_Gift(GiftID int, GiftCategory nvarchar(50), GiftStock int, GiftCoin int, ExchangeCount int, ExchangeCoin int, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Fact_Order(OrderID bigint, DateKey int, HourKey int, CustomerID int, AccountID int, OrderStatus int, TotalCoin int, GiftNum int, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Fact_BusinessCustomer(BusinessID int, CustomerID int, DateKey int, MemberCount int, CoinContribution int, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Fact_ProductCoin(ProductID int, BusinessID int, DateKey int, CodeCount int, UsedCodeCount int, UsedCoin int, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Fact_JFCode(JFCode nvarchar(64), ProductID int, DateKey int, JFStatus int, CodeCount int, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Fact_AccountTrade(TradeLogID int, DateKey int, HourKey int, AccountID int, BusinessID int NULL, ProductID int NULL, TradeType int, Coin int, OrderID bigint NULL, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Fact_AreaAnalysis(AreaID int, DateKey int, MemberCount int, OrderCount int, OrderCoin int, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
GO
