USE BI_GoldCoin_DW;
GO

DROP TABLE IF EXISTS dbo.Dim_Date,dbo.Dim_Hour,dbo.Dim_Business,dbo.Dim_Product,dbo.Dim_Customer,dbo.Dim_Gift,dbo.Dim_Area,dbo.Dim_JFCode,dbo.Dim_TradeType,dbo.Dim_OrderStatus;
GO

CREATE TABLE dbo.Dim_Date(DateKey int NOT NULL PRIMARY KEY, FullDate date NOT NULL, YearNo int, QuarterNo int, MonthNo int, DayNo int, WeekDayName nvarchar(20), ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Dim_Hour(HourKey int NOT NULL PRIMARY KEY, HourNo int NOT NULL, HourLabel nvarchar(20), ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Dim_Business(BusinessID int NOT NULL PRIMARY KEY, BusinessCnName nvarchar(100), BusinessEnName varchar(100), BusinessStatus tinyint, CreateTime datetime, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Dim_Product(ProductID int NOT NULL PRIMARY KEY, ProductName nvarchar(100), BusinessID int, ProductBrand nvarchar(100), ProductType nvarchar(100), ProductCoin int, ProductStatus int, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Dim_Customer(CustomerID int NOT NULL PRIMARY KEY, LoginName nvarchar(100), RealName nvarchar(100), Gender tinyint, AreaID int, RegType int, CusStatus int, FromBusiness int, CreateTime datetime, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Dim_Gift(GiftID int NOT NULL PRIMARY KEY, GiftName nvarchar(100), GiftCategory nvarchar(50), GfitCoin int, GiftNum int, GiftStatus int, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Dim_Area(AreaID int NOT NULL PRIMARY KEY, AreaName nvarchar(100), CityID int NULL, CityName nvarchar(100) NULL, ProvinceID int NULL, ProvinceName nvarchar(100) NULL, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Dim_JFCode(JFCode nvarchar(64) NOT NULL PRIMARY KEY, JFCode1 nvarchar(64), ProductID int, JFStatus int, ImportBatch int, CreateTime datetime, ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Dim_TradeType(TradeType int NOT NULL PRIMARY KEY, TradeTypeName nvarchar(30), ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
CREATE TABLE dbo.Dim_OrderStatus(OrderStatus int NOT NULL PRIMARY KEY, OrderStatusName nvarchar(30), ETL_LoadTime datetime NOT NULL DEFAULT GETDATE());
GO
