USE BIDemo_AccumulateCoin;
GO

SET NOCOUNT ON;

DECLARE @TargetBusiness int = 100, @TargetProduct int = 500, @TargetGift int = 100, @TargetJFCode int = 100000;
DECLARE @i int, @id int, @businessCount int, @productCount int, @giftCount int, @codeCount int;

SELECT @businessCount = COUNT(*) FROM dbo.BusinessMen;
SET @i = @businessCount + 1;
WHILE @i <= @TargetBusiness
BEGIN
    DECLARE @BusinessID int = ISNULL((SELECT MAX(BusinessID) FROM dbo.BusinessMen WITH (TABLOCKX)),0)+1;
    DECLARE @AccountID int = ISNULL((SELECT MAX(AccountID) FROM dbo.Account WITH (TABLOCKX)),0)+1;
    INSERT INTO dbo.BusinessMen(BusinessID,BusinessCnName,BusinessEnName,CreateTime,BusinessStatus,UpdateTime)
    VALUES(@BusinessID,N'模拟商家'+CAST(@i AS nvarchar(20)),'SeedBusiness'+CAST(@i AS varchar(20)),DATEADD(day,-ABS(CHECKSUM(NEWID()))%720,GETDATE()),1,GETDATE());
    INSERT INTO dbo.Account(AccountID,OwnerID,Acctype,CreateTime,AccStatus,ValidCoin,FrozenCoin,OnWayCoin,ExpireCoin,HistoryCoin)
    VALUES(@AccountID,@BusinessID,2,GETDATE(),1,0,0,0,0,0);
    SET @i += 1;
END

SELECT @productCount = COUNT(*) FROM dbo.ProductInfo;
SET @i = @productCount + 1;
WHILE @i <= @TargetProduct
BEGIN
    SELECT TOP 1 @id = BusinessID FROM dbo.BusinessMen ORDER BY NEWID();
    DECLARE @ProductID int = ISNULL((SELECT MAX(ProductID) FROM dbo.ProductInfo WITH (TABLOCKX)),0)+1;
    INSERT INTO dbo.ProductInfo(ProductID,ProductName,BusinessID,ProductBrand,ProductType,ProductCoin,ProductStatus,UpdateTime)
    VALUES(@ProductID,N'模拟积分商品'+CAST(@i AS nvarchar(20)),@id,N'GoldCoin',N'实训商品',10 + ABS(CHECKSUM(NEWID()))%500,1,GETDATE());
    SET @i += 1;
END

SELECT @giftCount = COUNT(*) FROM dbo.GiftInfo;
SET @i = @giftCount + 1;
WHILE @i <= @TargetGift
BEGIN
    DECLARE @GiftID int = ISNULL((SELECT MAX(GiftID) FROM dbo.GiftInfo WITH (TABLOCKX)),0)+1;
    INSERT INTO dbo.GiftInfo(GiftID,GiftName,CreateTime,GiftStatus,GfitCoin,GiftNum,GiftCategory)
    VALUES(@GiftID,N'模拟兑换礼品'+CAST(@i AS nvarchar(20)),GETDATE(),1,100 + ABS(CHECKSUM(NEWID()))%2000,100 + ABS(CHECKSUM(NEWID()))%900,N'实训礼品');
    SET @i += 1;
END

SELECT @codeCount = COUNT(*) FROM dbo.JFCode;
SET @i = @codeCount + 1;
WHILE @i <= @TargetJFCode
BEGIN
    SELECT TOP 1 @id = ProductID FROM dbo.ProductInfo ORDER BY NEWID();
    DECLARE @plain varchar(50) = 'BI' + CONVERT(varchar(8), GETDATE(), 112) + RIGHT('0000000000'+CAST(@i AS varchar(20)),10);
    IF NOT EXISTS (SELECT 1 FROM dbo.JFCode WHERE JFCode1=@plain)
    BEGIN
        INSERT INTO dbo.JFCode(JFCode,JFCode1,ProductID,JFStatus,CreateTime,EndTime,ImportBatch)
        VALUES(dbo.MD5(@plain,32),@plain,@id,1,DATEADD(day,-ABS(CHECKSUM(NEWID()))%365,GETDATE()),DATEADD(year,2,GETDATE()),20260706);
    END
    SET @i += 1;
END

SELECT 'BusinessMen' AS TableName, COUNT(*) AS TotalRows FROM dbo.BusinessMen
UNION ALL SELECT 'ProductInfo', COUNT(*) FROM dbo.ProductInfo
UNION ALL SELECT 'GiftInfo', COUNT(*) FROM dbo.GiftInfo
UNION ALL SELECT 'JFCode', COUNT(*) FROM dbo.JFCode;
GO
