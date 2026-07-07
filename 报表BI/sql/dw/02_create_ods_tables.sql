USE BI_GoldCoin_DW;
GO

DROP TABLE IF EXISTS dbo.ODS_CustomerInfo,dbo.ODS_BusinessMen,dbo.ODS_ProductInfo,dbo.ODS_GiftInfo,dbo.ODS_JFCode,dbo.ODS_Account,dbo.ODS_AccountTradeLog,dbo.ODS_AccountTradeIn,dbo.ODS_AccountTradeOut,dbo.ODS_OrderInfo,dbo.ODS_OrderGift,dbo.ODS_ProvinceInfo,dbo.ODS_CityInfo,dbo.ODS_AreaInfo;
GO

SELECT TOP 0
    CustomerID = CONVERT(int, CustomerID), LoginName, RealName, PWD, CreateTime, AreaID, Gender, Phone, Email, RegType, CusStatus, FromBusiness,
    Verstamp = CONVERT(varbinary(8), Verstamp),
    CAST(NULL AS datetime) AS ETL_LoadTime
INTO dbo.ODS_CustomerInfo
FROM BIDemo_AccumulateCoin.dbo.CustomerInfo;
SELECT TOP 0 *, CAST(NULL AS datetime) AS ETL_LoadTime INTO dbo.ODS_BusinessMen FROM BIDemo_AccumulateCoin.dbo.BusinessMen;
SELECT TOP 0 *, CAST(NULL AS datetime) AS ETL_LoadTime INTO dbo.ODS_ProductInfo FROM BIDemo_AccumulateCoin.dbo.ProductInfo;
SELECT TOP 0 *, CAST(NULL AS datetime) AS ETL_LoadTime INTO dbo.ODS_GiftInfo FROM BIDemo_AccumulateCoin.dbo.GiftInfo;
SELECT TOP 0 *, CAST(NULL AS datetime) AS ETL_LoadTime INTO dbo.ODS_JFCode FROM BIDemo_AccumulateCoin.dbo.JFCode;
SELECT TOP 0
    AccountID, OwnerID, Acctype, CreateTime, AccStatus, ValidCoin, FrozenCoin, OnWayCoin, ExpireCoin, HistoryCoin, LastAddCoinTime, LastConsumeTime,
    Verstamp = CONVERT(varbinary(8), Verstamp), CAST(NULL AS datetime) AS ETL_LoadTime
INTO dbo.ODS_Account
FROM BIDemo_AccumulateCoin.dbo.Account;
SELECT TOP 0
    TradeLogID = CONVERT(int, TradeLogID), CreateTime, TradeTime, JFCode, ProductID, BusinessID, TradeType, TradeMethod, OrderID, CancleTradeLogID,
    IsOnWay, IsCancled, Coin, AccountID, FrozenCoinBefore, FrozenCoinAfter, ValidCoinBefore, ValidCoinAfter, OnWayCoinBefore, OnWayCoinAfter,
    SourceTradelogID, Verstamp = CONVERT(varbinary(8), Verstamp), CAST(NULL AS datetime) AS ETL_LoadTime
INTO dbo.ODS_AccountTradeLog
FROM BIDemo_AccumulateCoin.dbo.AccountTradeLog;
SELECT TOP 0
    TradeID = CONVERT(int, TradeID), CreateTime, Coin, TotalCoin, AccountID, TargetAccountID, TradeOutLogID, TradeInLogID, TradeInTime,
    Verstamp = CONVERT(varbinary(8), Verstamp),
    CAST(NULL AS datetime) AS ETL_LoadTime
INTO dbo.ODS_AccountTradeIn
FROM BIDemo_AccumulateCoin.dbo.AccountTradeIn;
SELECT TOP 0
    TradeID = CONVERT(int, TradeID), CreateTime, Coin, TotalCoin, AccountID, TargetAccountID, TradeOutLogID, TradeInLogID, TradeInTime, TradeOutTime,
    Verstamp = CONVERT(varbinary(8), Verstamp),
    CAST(NULL AS datetime) AS ETL_LoadTime
INTO dbo.ODS_AccountTradeOut
FROM BIDemo_AccumulateCoin.dbo.AccountTradeOut;
SELECT TOP 0
    OrderID = CONVERT(bigint, OrderID), CreateTime, OrderTime, OrderStatus, AccountID, CustomerID, TotalCoin, DestCustomerName, DestAreaID,
    DestAddress, Dest_ZipCode, Dest_Tel, Verstamp = CONVERT(varbinary(8), Verstamp), CAST(NULL AS datetime) AS ETL_LoadTime
INTO dbo.ODS_OrderInfo
FROM BIDemo_AccumulateCoin.dbo.OrderInfo;
SELECT TOP 0
    OrderID, GiftID, CreateTime, GiftNum, GiftCoin, Coin, Verstamp = CONVERT(varbinary(8), Verstamp), CAST(NULL AS datetime) AS ETL_LoadTime
INTO dbo.ODS_OrderGift
FROM BIDemo_AccumulateCoin.dbo.OrderGift;
SELECT TOP 0 *, CAST(NULL AS datetime) AS ETL_LoadTime INTO dbo.ODS_ProvinceInfo FROM BIDemo_AccumulateCoin.dbo.ProvinceInfo;
SELECT TOP 0 *, CAST(NULL AS datetime) AS ETL_LoadTime INTO dbo.ODS_CityInfo FROM BIDemo_AccumulateCoin.dbo.CityInfo;
SELECT TOP 0 *, CAST(NULL AS datetime) AS ETL_LoadTime INTO dbo.ODS_AreaInfo FROM BIDemo_AccumulateCoin.dbo.AreaInfo;
GO
