from datetime import datetime

from db.sqlserver import execute, one, rows


PRODUCTS = [
    ("1.jpg", "9999金币", "小霸王K10全网通4G网络Wifi学习机"),
    ("2.jpg", "1478金币", "泰科拉时光机复古T038云山桃花芯"),
    ("3.jpg", "198金币", "现代简约ins风少女家用梳妆椅"),
    ("4.jpg", "7099金币", "Sharp 70寸4K网络智能液晶电视机"),
    ("5.jpg", "508金币", "BOLON偏光男士金属复古太阳镜"),
    ("6.jpg", "39999金币", "SCOTT 碳纤维软尾山地自行车"),
    ("7.jpg", "198金币", "Edifier W25BT蓝牙耳机"),
    ("8.jpg", "26625金币", "瑞士欧米茄碟飞系列机械男表"),
    ("9.jpg", "89金币", "浪莎纯棉百搭复古日系女中筒袜"),
]

CHANNELS = [
    ("非常大牌", "疯抢500积分金币", ["A.jpg", "B.jpg"]),
    ("极有家", "精致到一丝不苟的家", ["E.jpg", "D.jpg"]),
    ("生活家", "彩色绕线画 陪你看日出", ["I.jpg", "H.jpg"]),
    ("汇吃", "高颜值 好品质的食物", ["J.jpg", "F.jpg"]),
    ("苏宁易购", "1元预约最高抵900金币", ["C.jpg", "G.jpg"]),
]


def homepage_data():
    gifts = rows(
        """
        SELECT TOP 9 GiftID, GiftName, GfitCoin, GiftNum, GiftCategory
        FROM dbo.GiftInfo
        WHERE ISNULL(GiftStatus, 1) = 1
        ORDER BY GiftID DESC
        """
    )
    return {"products": PRODUCTS, "channels": CHANNELS, "gifts": gifts}


def register(form):
    execute(
        """
        DECLARE @AccountID int = ISNULL((SELECT MAX(AccountID) FROM dbo.Account WITH (TABLOCKX)),0)+1;
        INSERT INTO dbo.CustomerInfo
        (LoginName, RealName, PWD, CreateTime, Gender, Phone, Email, RegType, CusStatus)
        VALUES(?, ?, ?, GETDATE(), 1, ?, ?, 1, 1);
        DECLARE @CustomerID int = CONVERT(int, SCOPE_IDENTITY());
        INSERT INTO dbo.Account
        (AccountID, OwnerID, Acctype, CreateTime, AccStatus, ValidCoin, FrozenCoin, OnWayCoin, ExpireCoin, HistoryCoin)
        VALUES(@AccountID, @CustomerID, 1, GETDATE(), 1, 0, 0, 0, 0, 0);
        """,
        [form.get("login_name"), form.get("real_name"), form.get("password"), form.get("phone"), form.get("email")],
    )


def login(login_name, password):
    return one(
        """
        SELECT TOP 1 c.CustomerID, c.LoginName, c.RealName, c.Phone, c.Email, a.AccountID, a.ValidCoin
        FROM dbo.CustomerInfo c
        LEFT JOIN dbo.Account a ON a.OwnerID = c.CustomerID AND a.Acctype = 1
        WHERE c.LoginName = ? AND (c.PWD = ? OR ? = '')
        """,
        [login_name, password, password or ""],
    )


def profile(customer_id):
    member = one(
        """
        SELECT c.CustomerID, c.LoginName, c.RealName, c.Phone, c.Email, a.AccountID, a.ValidCoin
        FROM dbo.CustomerInfo c
        LEFT JOIN dbo.Account a ON a.OwnerID = c.CustomerID AND a.Acctype = 1
        WHERE c.CustomerID = ?
        """,
        [int(customer_id)],
    )
    orders = rows("SELECT TOP 20 OrderID, OrderTime, OrderStatus, TotalCoin FROM dbo.OrderInfo WHERE CustomerID=? ORDER BY OrderID DESC", [int(customer_id)])
    trades = rows("SELECT TOP 20 TradeLogID, TradeTime, TradeType, JFCode, Coin FROM dbo.AccountTradeLog WHERE AccountID=? ORDER BY TradeLogID DESC", [member["AccountID"] if member else 0])
    return member, orders, trades


def earn_coin(account_id, code):
    return one(
        """
        DECLARE @result int, @message nvarchar(100), @newTradeLogID int;
        EXEC dbo.CoinTrade ?, ?, ?, ?, ?, @result OUTPUT, @message OUTPUT, @newTradeLogID OUTPUT;
        SELECT @result AS result, @message AS message, @newTradeLogID AS trade_log_id;
        """,
        [int(account_id), 2, datetime.now(), code, 1],
    )


def gifts():
    return rows("SELECT TOP 80 GiftID, GiftName, GfitCoin, GiftNum, GiftCategory FROM dbo.GiftInfo WHERE ISNULL(GiftStatus,1)=1 ORDER BY GiftID DESC")


def checkout(customer_id, account_id, gift_id, qty):
    gift = one("SELECT GfitCoin FROM dbo.GiftInfo WHERE GiftID=?", [int(gift_id)])
    if not gift:
        return {"order_id": -1, "message": "礼品不存在或已下架。"}
    total = int(gift["GfitCoin"]) * int(qty)
    return one(
        """
        DECLARE @orderid bigint, @message nvarchar(100);
        EXEC dbo.AddOrder ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, @orderid OUTPUT, @message OUTPUT;
        SELECT @orderid AS order_id, @message AS message;
        """,
        [
            int(customer_id),
            int(account_id),
            datetime.now(),
            1,
            total,
            str(gift_id),
            str(qty),
            "金币联盟会员",
            1,
            "广东广州",
            "510000",
            "13800000000",
        ],
    )
