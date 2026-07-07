USE BI_GoldCoin_DW;
GO

DECLARE @now datetime = GETDATE();

TRUNCATE TABLE dbo.ODS_CustomerInfo; INSERT INTO dbo.ODS_CustomerInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.CustomerInfo;
TRUNCATE TABLE dbo.ODS_BusinessMen; INSERT INTO dbo.ODS_BusinessMen SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.BusinessMen;
TRUNCATE TABLE dbo.ODS_ProductInfo; INSERT INTO dbo.ODS_ProductInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.ProductInfo;
TRUNCATE TABLE dbo.ODS_GiftInfo; INSERT INTO dbo.ODS_GiftInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.GiftInfo;
TRUNCATE TABLE dbo.ODS_JFCode; INSERT INTO dbo.ODS_JFCode SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.JFCode;
TRUNCATE TABLE dbo.ODS_Account; INSERT INTO dbo.ODS_Account SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.Account;
TRUNCATE TABLE dbo.ODS_AccountTradeLog; INSERT INTO dbo.ODS_AccountTradeLog SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.AccountTradeLog;
TRUNCATE TABLE dbo.ODS_AccountTradeIn; INSERT INTO dbo.ODS_AccountTradeIn SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.AccountTradeIn;
TRUNCATE TABLE dbo.ODS_AccountTradeOut; INSERT INTO dbo.ODS_AccountTradeOut SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.AccountTradeOut;
TRUNCATE TABLE dbo.ODS_OrderInfo; INSERT INTO dbo.ODS_OrderInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.OrderInfo;
TRUNCATE TABLE dbo.ODS_OrderGift; INSERT INTO dbo.ODS_OrderGift SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.OrderGift;
TRUNCATE TABLE dbo.ODS_ProvinceInfo; INSERT INTO dbo.ODS_ProvinceInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.ProvinceInfo;
TRUNCATE TABLE dbo.ODS_CityInfo; INSERT INTO dbo.ODS_CityInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.CityInfo;
TRUNCATE TABLE dbo.ODS_AreaInfo; INSERT INTO dbo.ODS_AreaInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.AreaInfo;

TRUNCATE TABLE dbo.Dim_Date;
DECLARE @d date = DATEADD(year, -3, CAST(GETDATE() AS date));
WHILE @d <= DATEADD(year, 1, CAST(GETDATE() AS date))
BEGIN
    INSERT INTO dbo.Dim_Date(DateKey,FullDate,YearNo,QuarterNo,MonthNo,DayNo,WeekDayName)
    VALUES(CONVERT(int,CONVERT(varchar(8),@d,112)),@d,YEAR(@d),DATEPART(quarter,@d),MONTH(@d),DAY(@d),DATENAME(weekday,@d));
    SET @d = DATEADD(day,1,@d);
END

TRUNCATE TABLE dbo.Dim_Hour;
DECLARE @h int=0;
WHILE @h<24 BEGIN INSERT INTO dbo.Dim_Hour(HourKey,HourNo,HourLabel) VALUES(@h,@h,RIGHT('0'+CAST(@h AS varchar(2)),2)+':00'); SET @h+=1; END

TRUNCATE TABLE dbo.Dim_Business;
INSERT INTO dbo.Dim_Business(BusinessID,BusinessCnName,BusinessEnName,BusinessStatus,CreateTime)
SELECT BusinessID,BusinessCnName,BusinessEnName,BusinessStatus,CreateTime FROM dbo.ODS_BusinessMen;

TRUNCATE TABLE dbo.Dim_Product;
INSERT INTO dbo.Dim_Product(ProductID,ProductName,BusinessID,ProductBrand,ProductType,ProductCoin,ProductStatus)
SELECT ProductID,ProductName,BusinessID,ProductBrand,ProductType,ProductCoin,ProductStatus FROM dbo.ODS_ProductInfo;

TRUNCATE TABLE dbo.Dim_Customer;
INSERT INTO dbo.Dim_Customer(CustomerID,LoginName,RealName,Gender,AreaID,RegType,CusStatus,FromBusiness,CreateTime)
SELECT CustomerID,LoginName,RealName,Gender,AreaID,RegType,CusStatus,FromBusiness,CreateTime FROM dbo.ODS_CustomerInfo;

TRUNCATE TABLE dbo.Dim_Gift;
INSERT INTO dbo.Dim_Gift(GiftID,GiftName,GiftCategory,GfitCoin,GiftNum,GiftStatus)
SELECT GiftID,GiftName,GiftCategory,GfitCoin,GiftNum,GiftStatus FROM dbo.ODS_GiftInfo;

TRUNCATE TABLE dbo.Dim_Area;
INSERT INTO dbo.Dim_Area(AreaID,AreaName,CityID,CityName,ProvinceID,ProvinceName)
SELECT a.AreaID,a.AreaName,c.CityID,c.CityName,p.ProvinceID,p.ProvinceName
FROM dbo.ODS_AreaInfo a
LEFT JOIN dbo.ODS_CityInfo c ON c.CityID=a.CityID
LEFT JOIN dbo.ODS_ProvinceInfo p ON p.ProvinceID=c.ProvinceID;

TRUNCATE TABLE dbo.Dim_JFCode;
INSERT INTO dbo.Dim_JFCode(JFCode,JFCode1,ProductID,JFStatus,ImportBatch,CreateTime)
SELECT JFCode,JFCode1,ProductID,JFStatus,ImportBatch,CreateTime FROM dbo.ODS_JFCode;

TRUNCATE TABLE dbo.Dim_TradeType;
INSERT INTO dbo.Dim_TradeType(TradeType,TradeTypeName) VALUES(0,N'取消订单'),(1,N'兑换礼品'),(2,N'积分累加');

TRUNCATE TABLE dbo.Dim_OrderStatus;
INSERT INTO dbo.Dim_OrderStatus(OrderStatus,OrderStatusName) VALUES(1,N'订单生成配送中'),(2,N'审核通过'),(3,N'余额不足取消'),(4,N'客户取消'),(5,N'订单完成');

TRUNCATE TABLE dbo.Fact_Business;
INSERT INTO dbo.Fact_Business(BusinessID,DateKey,BusinessCount,EnabledBusinessCount,DisabledBusinessCount,ProductCount)
SELECT b.BusinessID, CONVERT(int,CONVERT(varchar(8),ISNULL(b.CreateTime,GETDATE()),112)), 1,
       CASE WHEN ISNULL(b.BusinessStatus,1)=1 THEN 1 ELSE 0 END,
       CASE WHEN ISNULL(b.BusinessStatus,1)<>1 THEN 1 ELSE 0 END,
       COUNT(p.ProductID)
FROM dbo.ODS_BusinessMen b LEFT JOIN dbo.ODS_ProductInfo p ON p.BusinessID=b.BusinessID
GROUP BY b.BusinessID,b.CreateTime,b.BusinessStatus;

TRUNCATE TABLE dbo.Fact_Customer;
INSERT INTO dbo.Fact_Customer(CustomerID,DateKey,AreaID,FromBusiness,CustomerCount,ValidCoin)
SELECT c.CustomerID, CONVERT(int,CONVERT(varchar(8),ISNULL(c.CreateTime,GETDATE()),112)), c.AreaID, c.FromBusiness, 1, ISNULL(a.ValidCoin,0)
FROM dbo.ODS_CustomerInfo c LEFT JOIN dbo.ODS_Account a ON a.OwnerID=c.CustomerID AND a.Acctype=1;

TRUNCATE TABLE dbo.Fact_Gift;
INSERT INTO dbo.Fact_Gift(GiftID,GiftCategory,GiftStock,GiftCoin,ExchangeCount,ExchangeCoin)
SELECT g.GiftID,g.GiftCategory,ISNULL(g.GiftNum,0),ISNULL(g.GfitCoin,0),ISNULL(SUM(og.GiftNum),0),ISNULL(SUM(og.Coin),0)
FROM dbo.ODS_GiftInfo g LEFT JOIN dbo.ODS_OrderGift og ON og.GiftID=g.GiftID
GROUP BY g.GiftID,g.GiftCategory,g.GiftNum,g.GfitCoin;

TRUNCATE TABLE dbo.Fact_Order;
INSERT INTO dbo.Fact_Order(OrderID,DateKey,HourKey,CustomerID,AccountID,OrderStatus,TotalCoin,GiftNum)
SELECT o.OrderID, CONVERT(int,CONVERT(varchar(8),ISNULL(o.OrderTime,o.CreateTime),112)), DATEPART(hour,ISNULL(o.OrderTime,o.CreateTime)),
       o.CustomerID,o.AccountID,o.OrderStatus,o.TotalCoin,ISNULL(SUM(og.GiftNum),0)
FROM dbo.ODS_OrderInfo o LEFT JOIN dbo.ODS_OrderGift og ON og.OrderID=o.OrderID
GROUP BY o.OrderID,o.OrderTime,o.CreateTime,o.CustomerID,o.AccountID,o.OrderStatus,o.TotalCoin;

TRUNCATE TABLE dbo.Fact_BusinessCustomer;
INSERT INTO dbo.Fact_BusinessCustomer(BusinessID,CustomerID,DateKey,MemberCount,CoinContribution)
SELECT l.BusinessID, a.OwnerID, CONVERT(int,CONVERT(varchar(8),ISNULL(l.TradeTime,l.CreateTime),112)), 1, SUM(ISNULL(l.Coin,0))
FROM dbo.ODS_AccountTradeLog l
JOIN dbo.ODS_Account a ON a.AccountID=l.AccountID AND a.Acctype=1
WHERE l.BusinessID IS NOT NULL
GROUP BY l.BusinessID,a.OwnerID,CONVERT(int,CONVERT(varchar(8),ISNULL(l.TradeTime,l.CreateTime),112));

TRUNCATE TABLE dbo.Fact_ProductCoin;
INSERT INTO dbo.Fact_ProductCoin(ProductID,BusinessID,DateKey,CodeCount,UsedCodeCount,UsedCoin)
SELECT p.ProductID,p.BusinessID,CONVERT(int,CONVERT(varchar(8),GETDATE(),112)),COUNT(c.JFCode),SUM(CASE WHEN c.JFStatus=2 THEN 1 ELSE 0 END),SUM(CASE WHEN c.JFStatus=2 THEN ISNULL(p.ProductCoin,0) ELSE 0 END)
FROM dbo.ODS_ProductInfo p LEFT JOIN dbo.ODS_JFCode c ON c.ProductID=p.ProductID
GROUP BY p.ProductID,p.BusinessID;

TRUNCATE TABLE dbo.Fact_JFCode;
INSERT INTO dbo.Fact_JFCode(JFCode,ProductID,DateKey,JFStatus,CodeCount)
SELECT JFCode,ProductID,CONVERT(int,CONVERT(varchar(8),ISNULL(CreateTime,GETDATE()),112)),JFStatus,1 FROM dbo.ODS_JFCode;

TRUNCATE TABLE dbo.Fact_AccountTrade;
INSERT INTO dbo.Fact_AccountTrade(TradeLogID,DateKey,HourKey,AccountID,BusinessID,ProductID,TradeType,Coin,OrderID)
SELECT TradeLogID,CONVERT(int,CONVERT(varchar(8),ISNULL(TradeTime,CreateTime),112)),DATEPART(hour,ISNULL(TradeTime,CreateTime)),AccountID,BusinessID,ProductID,TradeType,Coin,OrderID
FROM dbo.ODS_AccountTradeLog;

TRUNCATE TABLE dbo.Fact_AreaAnalysis;
INSERT INTO dbo.Fact_AreaAnalysis(AreaID,DateKey,MemberCount,OrderCount,OrderCoin)
SELECT ISNULL(c.AreaID,0), CONVERT(int,CONVERT(varchar(8),GETDATE(),112)), COUNT(DISTINCT c.CustomerID), COUNT(DISTINCT o.OrderID), ISNULL(SUM(o.TotalCoin),0)
FROM dbo.ODS_CustomerInfo c LEFT JOIN dbo.ODS_OrderInfo o ON o.CustomerID=c.CustomerID
GROUP BY ISNULL(c.AreaID,0);

MERGE dbo.ETL_Control AS t
USING (SELECT N'full_etl' AS TaskName) AS s ON t.TaskName=s.TaskName
WHEN MATCHED THEN UPDATE SET LastExtractTime=@now, CurrentExtractTime=@now, Status=N'Success', Message=N'Full ETL completed', UpdateTime=GETDATE()
WHEN NOT MATCHED THEN INSERT(TaskName,LastExtractTime,CurrentExtractTime,Status,Message) VALUES(N'full_etl',@now,@now,N'Success',N'Full ETL completed');
GO
