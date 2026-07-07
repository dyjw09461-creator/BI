USE BIDemo_AccumulateCoin;
GO

CREATE OR ALTER PROCEDURE dbo.usp_RegisterCustomer
    @LoginName nvarchar(50),
    @RealName nvarchar(50),
    @PWD varchar(50),
    @Gender tinyint,
    @Phone varchar(20),
    @Email varchar(100),
    @CustomerID int OUTPUT,
    @Msg nvarchar(100) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @AccountID int;
    BEGIN TRY
        BEGIN TRAN;
        IF EXISTS (SELECT 1 FROM dbo.CustomerInfo WHERE LoginName=@LoginName)
        BEGIN SET @Msg=N'登录名已经存在'; ROLLBACK TRAN; RETURN; END
        SELECT @AccountID = ISNULL(MAX(AccountID),0)+1 FROM dbo.Account WITH (TABLOCKX);
        INSERT INTO dbo.CustomerInfo
        (LoginName,RealName,PWD,CreateTime,Gender,Phone,Email,RegType,CusStatus)
        VALUES(@LoginName,@RealName,@PWD,GETDATE(),@Gender,@Phone,@Email,1,1);
        SET @CustomerID = CONVERT(int, SCOPE_IDENTITY());
        INSERT INTO dbo.Account
        (AccountID,OwnerID,Acctype,CreateTime,AccStatus,ValidCoin,FrozenCoin,OnWayCoin,ExpireCoin,HistoryCoin)
        VALUES(@AccountID,@CustomerID,1,GETDATE(),1,0,0,0,0,0);
        COMMIT TRAN;
        SET @Msg=N'会员注册成功';
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        SET @Msg=ERROR_MESSAGE();
    END CATCH
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_RegisterBusiness
    @BusinessCnName nvarchar(50),
    @BusinessEnName varchar(50),
    @BusinessID int OUTPUT,
    @Msg nvarchar(100) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @AccountID int;
    BEGIN TRY
        BEGIN TRAN;
        SELECT @BusinessID = ISNULL(MAX(BusinessID),0)+1 FROM dbo.BusinessMen WITH (TABLOCKX);
        SELECT @AccountID = ISNULL(MAX(AccountID),0)+1 FROM dbo.Account WITH (TABLOCKX);
        INSERT INTO dbo.BusinessMen
        (BusinessID,BusinessCnName,BusinessEnName,CreateTime,BusinessStatus,UpdateTime)
        VALUES(@BusinessID,@BusinessCnName,@BusinessEnName,GETDATE(),1,GETDATE());
        INSERT INTO dbo.Account
        (AccountID,OwnerID,Acctype,CreateTime,AccStatus,ValidCoin,FrozenCoin,OnWayCoin,ExpireCoin,HistoryCoin)
        VALUES(@AccountID,@BusinessID,2,GETDATE(),1,0,0,0,0,0);
        COMMIT TRAN;
        SET @Msg=N'商家注册成功';
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        SET @Msg=ERROR_MESSAGE();
    END CATCH
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_AddProduct
    @ProductName nvarchar(50),
    @BusinessID int,
    @ProductBrand nvarchar(50),
    @ProductType nvarchar(50),
    @ProductCoin int,
    @ProductID int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @ProductID = ISNULL(MAX(ProductID),0)+1 FROM dbo.ProductInfo WITH (TABLOCKX);
    INSERT INTO dbo.ProductInfo
    (ProductID,ProductName,BusinessID,ProductBrand,ProductType,ProductCoin,ProductStatus,UpdateTime)
    VALUES(@ProductID,@ProductName,@BusinessID,@ProductBrand,@ProductType,@ProductCoin,1,GETDATE());
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_AddGift
    @GiftName nvarchar(100),
    @GfitCoin int,
    @GiftNum int,
    @GiftCategory nvarchar(20),
    @GiftID int OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @GiftID = ISNULL(MAX(GiftID),0)+1 FROM dbo.GiftInfo WITH (TABLOCKX);
    INSERT INTO dbo.GiftInfo
    (GiftID,GiftName,CreateTime,GiftStatus,GfitCoin,GiftNum,GiftCategory)
    VALUES(@GiftID,@GiftName,GETDATE(),1,@GfitCoin,@GiftNum,@GiftCategory);
END;
GO

CREATE OR ALTER PROCEDURE dbo.usp_AddJFCodeBatch
    @ProductID int,
    @Prefix varchar(20),
    @Count int,
    @ImportBatch int
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @i int = 1, @code varchar(50);
    WHILE @i <= @Count
    BEGIN
        SET @code = @Prefix + RIGHT('00000000' + CAST(@i AS varchar(12)), 8) + RIGHT(REPLACE(CONVERT(varchar(36), NEWID()), '-', ''), 6);
        IF NOT EXISTS (SELECT 1 FROM dbo.JFCode WHERE JFCode1=@code)
        BEGIN
            INSERT INTO dbo.JFCode
            (JFCode,JFCode1,ProductID,JFStatus,CreateTime,EndTime,ImportBatch)
            VALUES(dbo.MD5(@code,32),@code,@ProductID,1,GETDATE(),DATEADD(year,2,GETDATE()),@ImportBatch);
        END
        SET @i += 1;
    END
END;
GO
