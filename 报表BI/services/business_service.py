from db.sqlserver import execute, one, rows


def require_text(form, key, label):
    value = (form.get(key) or "").strip()
    if not value:
        raise ValueError(f"{label}不能为空。")
    return value


def require_int(form, key, label, minimum=None):
    raw = (form.get(key) or "").strip()
    if not raw:
        raise ValueError(f"{label}不能为空。")
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{label}必须填写数字，当前输入为“{raw}”。") from exc
    if minimum is not None and value < minimum:
        raise ValueError(f"{label}不能小于 {minimum}。")
    return value


def optional_int(form, key, label, default, minimum=None):
    raw = (form.get(key) or "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{label}必须填写数字，当前输入为“{raw}”。") from exc
    if minimum is not None and value < minimum:
        raise ValueError(f"{label}不能小于 {minimum}。")
    return value


def counts():
    names = [
        "CustomerInfo",
        "BusinessMen",
        "ProductInfo",
        "GiftInfo",
        "JFCode",
        "OrderInfo",
        "OrderGift",
        "AccountTradeLog",
    ]
    return {name: one(f"SELECT COUNT(*) AS c FROM dbo.{name}")["c"] for name in names}


def dashboard():
    return {
        "counts": counts(),
        "jf_status": rows(
            """
            SELECT JFStatus AS status, COUNT(*) AS total
            FROM dbo.JFCode
            GROUP BY JFStatus
            ORDER BY JFStatus
            """
        ),
        "order_trend": rows(
            """
            SELECT TOP 14 CONVERT(varchar(10), COALESCE(OrderTime, CreateTime), 120) AS d,
                   COUNT(*) AS total
            FROM dbo.OrderInfo
            GROUP BY CONVERT(varchar(10), COALESCE(OrderTime, CreateTime), 120)
            ORDER BY d DESC
            """
        ),
    }


def list_customers(q=""):
    like = f"%{q}%"
    return rows(
        """
        SELECT TOP 200 c.CustomerID, c.LoginName, c.RealName, c.Phone, c.Email,
               c.CreateTime, a.AccountID, a.ValidCoin
        FROM dbo.CustomerInfo c
        LEFT JOIN dbo.Account a ON a.OwnerID = c.CustomerID AND a.Acctype = 1
        WHERE ? = '' OR c.LoginName LIKE ? OR c.RealName LIKE ? OR c.Phone LIKE ?
        ORDER BY c.CustomerID DESC
        """,
        [q, like, like, like],
    )


def create_customer(form):
    login_name = require_text(form, "login_name", "登录名")
    real_name = require_text(form, "real_name", "真实姓名")
    gender = optional_int(form, "gender", "性别", 1)
    execute(
        """
        DECLARE @AccountID int = ISNULL((SELECT MAX(AccountID) FROM dbo.Account WITH (TABLOCKX)),0)+1;
        INSERT INTO dbo.CustomerInfo
        (LoginName, RealName, PWD, CreateTime, Gender, Phone, Email, RegType, CusStatus, FromBusiness)
        VALUES
        (?, ?, ?, GETDATE(), ?, ?, ?, 1, 1, NULL);
        DECLARE @CustomerID int = CONVERT(int, SCOPE_IDENTITY());
        INSERT INTO dbo.Account
        (AccountID, OwnerID, Acctype, CreateTime, AccStatus, ValidCoin, FrozenCoin, OnWayCoin, ExpireCoin, HistoryCoin)
        VALUES
        (@AccountID, @CustomerID, 1, GETDATE(), 1, 0, 0, 0, 0, 0);
        """,
        [
            login_name,
            real_name,
            form.get("password") or "123456",
            gender,
            form.get("phone"),
            form.get("email"),
        ],
    )


def list_businesses(q=""):
    like = f"%{q}%"
    return rows(
        """
        SELECT TOP 200 b.BusinessID, b.BusinessCnName, b.BusinessEnName,
               b.BusinessStatus, b.CreateTime, a.AccountID, a.ValidCoin
        FROM dbo.BusinessMen b
        LEFT JOIN dbo.Account a ON a.OwnerID = b.BusinessID AND a.Acctype = 2
        WHERE ? = '' OR b.BusinessCnName LIKE ? OR b.BusinessEnName LIKE ?
        ORDER BY b.BusinessID DESC
        """,
        [q, like, like],
    )


def create_business(form):
    name = require_text(form, "name", "商家中文名")
    execute(
        """
        DECLARE @BusinessID int = ISNULL((SELECT MAX(BusinessID) FROM dbo.BusinessMen WITH (TABLOCKX)),0)+1;
        DECLARE @AccountID int = ISNULL((SELECT MAX(AccountID) FROM dbo.Account WITH (TABLOCKX)),0)+1;
        INSERT INTO dbo.BusinessMen
        (BusinessID, BusinessCnName, BusinessEnName, CreateTime, BusinessStatus, UpdateTime, UpdateUser)
        VALUES
        (@BusinessID, ?, ?, GETDATE(), 1, GETDATE(), NULL);
        INSERT INTO dbo.Account
        (AccountID, OwnerID, Acctype, CreateTime, AccStatus, ValidCoin, FrozenCoin, OnWayCoin, ExpireCoin, HistoryCoin)
        VALUES
        (@AccountID, @BusinessID, 2, GETDATE(), 1, 0, 0, 0, 0, 0);
        """,
        [name, form.get("en_name")],
    )


def list_products(q=""):
    like = f"%{q}%"
    return rows(
        """
        SELECT TOP 250 p.ProductID, p.ProductName, p.ProductBrand, p.ProductType,
               p.ProductCoin, p.ProductStatus, b.BusinessCnName
        FROM dbo.ProductInfo p
        LEFT JOIN dbo.BusinessMen b ON b.BusinessID = p.BusinessID
        WHERE ? = '' OR p.ProductName LIKE ? OR b.BusinessCnName LIKE ?
        ORDER BY p.ProductID DESC
        """,
        [q, like, like],
    )


def create_product(form):
    name = require_text(form, "name", "商品名")
    business_id = require_int(form, "business_id", "商家ID", 1)
    coin = optional_int(form, "coin", "商品积分", 0, 0)
    execute(
        """
        DECLARE @ProductID int = ISNULL((SELECT MAX(ProductID) FROM dbo.ProductInfo WITH (TABLOCKX)),0)+1;
        INSERT INTO dbo.ProductInfo
        (ProductID, ProductName, BusinessID, ProductBrand, ProductType, ProductCoin, ProductStatus, UpdateTime, UpdateUser)
        VALUES
        (@ProductID, ?, ?, ?, ?, ?, 1, GETDATE(), NULL);
        """,
        [
            name,
            business_id,
            form.get("brand"),
            form.get("type"),
            coin,
        ],
    )


def list_gifts(q=""):
    like = f"%{q}%"
    return rows(
        """
        SELECT TOP 250 GiftID, GiftName, GiftCategory, GfitCoin, GiftNum, GiftStatus, CreateTime
        FROM dbo.GiftInfo
        WHERE ? = '' OR GiftName LIKE ? OR GiftCategory LIKE ?
        ORDER BY GiftID DESC
        """,
        [q, like, like],
    )


def create_gift(form):
    name = require_text(form, "name", "礼品名")
    coin = optional_int(form, "coin", "兑换金币", 0, 0)
    num = optional_int(form, "num", "库存", 0, 0)
    execute(
        """
        DECLARE @GiftID int = ISNULL((SELECT MAX(GiftID) FROM dbo.GiftInfo WITH (TABLOCKX)),0)+1;
        INSERT INTO dbo.GiftInfo
        (GiftID, GiftName, CreateTime, GiftStatus, GfitCoin, GiftNum, GiftCategory)
        VALUES
        (@GiftID, ?, GETDATE(), 1, ?, ?, ?);
        """,
        [name, coin, num, form.get("category")],
    )


def list_codes(q=""):
    like = f"%{q}%"
    return rows(
        """
        SELECT TOP 300 c.JFCode1, c.ProductID, p.ProductName, c.JFStatus, c.CreateTime, c.EndTime, c.ImportBatch
        FROM dbo.JFCode c
        LEFT JOIN dbo.ProductInfo p ON p.ProductID = c.ProductID
        WHERE ? = '' OR c.JFCode1 LIKE ? OR p.ProductName LIKE ?
        ORDER BY c.CreateTime DESC
        """,
        [q, like, like],
    )


def create_code(form):
    code = require_text(form, "code", "明文积分码")
    product_id = require_int(form, "product_id", "商品ID", 1)
    batch = optional_int(form, "batch", "批次", 1, 1)
    execute(
        """
        INSERT INTO dbo.JFCode
        (JFCode, JFCode1, ProductID, JFStatus, CreateTime, EndTime, ImportBatch, CreateUserID)
        VALUES
        (dbo.MD5(?, 32), ?, ?, 1, GETDATE(), DATEADD(year, 2, GETDATE()), ?, NULL);
        """,
        [code, code, product_id, batch],
    )


def earn_coin(account_id, code):
    return one(
        """
        DECLARE @result int, @message nvarchar(100), @newTradeLogID int;
        EXEC dbo.CoinTrade ?, 2, GETDATE(), ?, 1, @result OUTPUT, @message OUTPUT, @newTradeLogID OUTPUT;
        SELECT @result AS result, @message AS message, @newTradeLogID AS trade_log_id;
        """,
        [int(account_id), code],
    )


def exchange_gift(customer_id, account_id, gift_id, gift_num):
    gift = one("SELECT GfitCoin FROM dbo.GiftInfo WHERE GiftID = ?", [int(gift_id)])
    total_coin = int(gift["GfitCoin"]) * int(gift_num)
    return one(
        """
        DECLARE @orderid bigint, @message nvarchar(100);
        EXEC dbo.AddOrder ?, ?, GETDATE(), 1, ?, ?, ?, N'实训用户', 1, N'实训地址', N'510000', '13800000000',
             @orderid OUTPUT, @message OUTPUT;
        SELECT @orderid AS order_id, @message AS message;
        """,
        [int(customer_id), int(account_id), total_coin, str(gift_id), str(gift_num)],
    )


def list_orders():
    return rows(
        """
        SELECT TOP 200 o.OrderID, o.OrderTime, o.OrderStatus, o.CustomerID, o.AccountID,
               o.TotalCoin, c.LoginName, COUNT(g.GiftID) AS GiftLines
        FROM dbo.OrderInfo o
        LEFT JOIN dbo.CustomerInfo c ON c.CustomerID = o.CustomerID
        LEFT JOIN dbo.OrderGift g ON g.OrderID = o.OrderID
        GROUP BY o.OrderID, o.OrderTime, o.OrderStatus, o.CustomerID, o.AccountID, o.TotalCoin, c.LoginName
        ORDER BY o.OrderID DESC
        """
    )


def list_trades():
    return rows(
        """
        SELECT TOP 300 TradeLogID, TradeTime, JFCode, ProductID, BusinessID, TradeType,
               TradeMethod, OrderID, Coin, AccountID, ValidCoinBefore, ValidCoinAfter
        FROM dbo.AccountTradeLog
        ORDER BY TradeLogID DESC
        """
    )
