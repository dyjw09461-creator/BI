USE BI_GoldCoin_DW;
GO

DECLARE @last datetime = ISNULL((SELECT LastExtractTime FROM dbo.ETL_Control WHERE TaskName=N'incremental_etl'), '19000101');
DECLARE @now datetime = GETDATE();

INSERT INTO dbo.ODS_CustomerInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.CustomerInfo WHERE ISNULL(CreateTime,'19000101') > @last;
INSERT INTO dbo.ODS_BusinessMen SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.BusinessMen WHERE ISNULL(UpdateTime,CreateTime) > @last;
INSERT INTO dbo.ODS_ProductInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.ProductInfo WHERE ISNULL(UpdateTime,'19000101') > @last;
INSERT INTO dbo.ODS_GiftInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.GiftInfo WHERE ISNULL(CreateTime,'19000101') > @last;
INSERT INTO dbo.ODS_JFCode SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.JFCode WHERE ISNULL(UpdateTime,CreateTime) > @last;
INSERT INTO dbo.ODS_OrderInfo SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.OrderInfo WHERE ISNULL(OrderTime,CreateTime) > @last;
INSERT INTO dbo.ODS_OrderGift SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.OrderGift WHERE ISNULL(CreateTime,'19000101') > @last;
INSERT INTO dbo.ODS_AccountTradeLog SELECT *, @now FROM BIDemo_AccumulateCoin.dbo.AccountTradeLog WHERE ISNULL(TradeTime,CreateTime) > @last;

MERGE dbo.ETL_Control AS t
USING (SELECT N'incremental_etl' AS TaskName) AS s ON t.TaskName=s.TaskName
WHEN MATCHED THEN UPDATE SET LastExtractTime=@now, CurrentExtractTime=@now, Status=N'Success', Message=N'ODS incremental append completed; run full ETL to rebuild facts for demo consistency', UpdateTime=GETDATE()
WHEN NOT MATCHED THEN INSERT(TaskName,LastExtractTime,CurrentExtractTime,Status,Message) VALUES(N'incremental_etl',@now,@now,N'Success',N'ODS incremental append completed');
GO
