IF DB_ID(N'BI_GoldCoin_DW') IS NULL
BEGIN
    CREATE DATABASE BI_GoldCoin_DW;
END
GO

USE BI_GoldCoin_DW;
GO

IF OBJECT_ID('dbo.ETL_Control','U') IS NULL
BEGIN
    CREATE TABLE dbo.ETL_Control(
        TaskName nvarchar(80) NOT NULL PRIMARY KEY,
        LastExtractTime datetime NULL,
        CurrentExtractTime datetime NULL,
        Status nvarchar(20) NULL,
        Message nvarchar(400) NULL,
        UpdateTime datetime NOT NULL DEFAULT GETDATE()
    );
END
GO
