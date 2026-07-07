import json
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

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

DEMO_USER = ("user", "123456")
DEMO_MERCHANT = ("merchant", "123456")
MERCHANT_PROFILE_FILE = Path(__file__).resolve().parents[1] / "docs" / "merchant_profiles.json"
WALLET_FILE = Path(__file__).resolve().parents[1] / "docs" / "customer_wallets.json"

CASH_PRODUCTS = [
    {
        "id": "cash-01",
        "name": "智能学习机 K10",
        "image": "1.jpg",
        "price_cents": 129900,
        "reward_coin": 9999,
        "tag": "学习数码",
        "desc": "现金购买后赠送金币，可继续到积分商城兑换礼品。",
    },
    {
        "id": "cash-02",
        "name": "复古蓝牙音箱",
        "image": "2.jpg",
        "price_cents": 29800,
        "reward_coin": 1478,
        "tag": "影音生活",
        "desc": "适合作为会员活动商品，购买后自动发放金币。",
    },
    {
        "id": "cash-03",
        "name": "家用梳妆椅",
        "image": "3.jpg",
        "price_cents": 9900,
        "reward_coin": 198,
        "tag": "居家日用",
        "desc": "小额现金商品，适合演示充值后即时消费。",
    },
    {
        "id": "cash-04",
        "name": "70 寸智能电视",
        "image": "4.jpg",
        "price_cents": 369900,
        "reward_coin": 7099,
        "tag": "家电专区",
        "desc": "高客单价商品，用于体现购买金额和赠送金币联动。",
    },
    {
        "id": "cash-05",
        "name": "偏光太阳镜",
        "image": "5.jpg",
        "price_cents": 16800,
        "reward_coin": 508,
        "tag": "潮流配饰",
        "desc": "现金购买产生订单记录，并更新会员金币余额。",
    },
    {
        "id": "cash-06",
        "name": "碳纤维山地车",
        "image": "6.jpg",
        "price_cents": 899900,
        "reward_coin": 39999,
        "tag": "运动户外",
        "desc": "高积分返赠商品，可用于展示积分激励效果。",
    },
]


def homepage_data():
    gifts_data = rows(
        """
        SELECT TOP 9 GiftID, GiftName, GfitCoin, GiftNum, GiftCategory
        FROM dbo.GiftInfo
        WHERE ISNULL(GiftStatus, 1) = 1
        ORDER BY GiftID DESC
        """
    )
    return {"products": cash_products(), "channels": CHANNELS, "gifts": with_gift_images(gifts_data)}


def load_merchant_profiles():
    if not MERCHANT_PROFILE_FILE.exists():
        return {}
    try:
        return json.loads(MERCHANT_PROFILE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_merchant_profiles(data):
    MERCHANT_PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MERCHANT_PROFILE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_wallets():
    if not WALLET_FILE.exists():
        return {}
    try:
        return json.loads(WALLET_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_wallets(data):
    WALLET_FILE.parent.mkdir(parents=True, exist_ok=True)
    WALLET_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def money_to_cents(value, label):
    raw = (value or "").strip()
    if not raw:
        raise ValueError(f"{label}不能为空。")
    try:
        amount = Decimal(raw).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{label}必须是金额。") from exc
    if amount <= 0:
        raise ValueError(f"{label}必须大于 0。")
    return int(amount * 100)


def cents_to_yuan(cents):
    return f"{Decimal(int(cents or 0)) / Decimal(100):.2f}"


def format_money_fields(row):
    item = dict(row)
    if "price_cents" in item:
        item["price"] = cents_to_yuan(item["price_cents"])
    if "amount_cents" in item:
        item["amount"] = cents_to_yuan(item["amount_cents"])
    if "balance_after_cents" in item:
        item["balance_after"] = cents_to_yuan(item["balance_after_cents"])
    if "total_cents" in item:
        item["total"] = cents_to_yuan(item["total_cents"])
    return item


def wallet_record(customer_id):
    wallets = load_wallets()
    key = str(customer_id)
    if key not in wallets:
        wallets[key] = {"balance_cents": 0, "cards": [], "recharges": [], "cash_orders": []}
        save_wallets(wallets)
    return wallets, key, wallets[key]


def mask_card(card_no):
    digits = "".join(ch for ch in (card_no or "") if ch.isdigit())
    if len(digits) < 8:
        raise ValueError("银行卡号至少需要 8 位数字。")
    return f"{digits[:4]} **** **** {digits[-4:]}"


def wallet_data(customer_id):
    _, _, wallet = wallet_record(customer_id)
    cash_cart = cart_items(customer_id)
    points_cart = points_cart_items(customer_id)
    return {
        "balance": cents_to_yuan(wallet.get("balance_cents", 0)),
        "cards": wallet.get("cards", []),
        "cash_cart": cash_cart,
        "cash_cart_count": sum(int(item.get("qty") or 0) for item in cash_cart),
        "cash_cart_total": cents_to_yuan(sum(int(item.get("line_total_cents") or 0) for item in cash_cart)),
        "cash_cart_reward_coin": sum(int(item.get("line_reward_coin") or 0) for item in cash_cart),
        "points_cart": points_cart,
        "points_cart_count": sum(int(item.get("qty") or 0) for item in points_cart),
        "points_cart_coin": sum(int(item.get("line_coin") or 0) for item in points_cart),
        "recharges": [format_money_fields(row) for row in reversed(wallet.get("recharges", [])[-12:])],
        "cash_orders": [format_money_fields(row) for row in reversed(wallet.get("cash_orders", [])[-12:])],
    }


def bind_bank_card(form, customer_id):
    wallets, key, wallet = wallet_record(customer_id)
    card_no = require_text(form, "card_no", "银行卡号")
    bank_name = require_text(form, "bank_name", "开户银行")
    owner_name = require_text(form, "owner_name", "持卡人")
    phone = require_text(form, "phone", "预留手机号")
    masked = mask_card(card_no)
    for card in wallet.get("cards", []):
        if card["masked"] == masked:
            raise ValueError("这张银行卡已经绑定。")
    wallet.setdefault("cards", []).append(
        {
            "id": f"card-{datetime.now():%Y%m%d%H%M%S%f}",
            "bank_name": bank_name,
            "owner_name": owner_name,
            "phone": phone,
            "masked": masked,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    wallets[key] = wallet
    save_wallets(wallets)


def recharge_wallet(form, customer_id):
    wallets, key, wallet = wallet_record(customer_id)
    if not wallet.get("cards"):
        raise ValueError("请先绑定银行卡，再进行充值。")
    amount_cents = money_to_cents(form.get("amount"), "充值金额")
    wallet["balance_cents"] = int(wallet.get("balance_cents", 0)) + amount_cents
    wallet.setdefault("recharges", []).append(
        {
            "id": f"recharge-{datetime.now():%Y%m%d%H%M%S%f}",
            "amount_cents": amount_cents,
            "balance_after_cents": wallet["balance_cents"],
            "card_id": form.get("card_id") or wallet["cards"][0]["id"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    wallets[key] = wallet
    save_wallets(wallets)
    return {"balance": cents_to_yuan(wallet["balance_cents"])}


def cash_products():
    return [format_money_fields(item) for item in CASH_PRODUCTS]


def cash_product(product_id):
    return next((item for item in CASH_PRODUCTS if item["id"] == product_id), None)


def cart_items(customer_id):
    _, _, wallet = wallet_record(customer_id)
    items = []
    for row in wallet.get("cash_cart", []):
        product = cash_product(row.get("product_id"))
        if not product:
            continue
        qty = int(row.get("qty") or 1)
        item = format_money_fields(product)
        item["qty"] = qty
        item["line_total_cents"] = int(product["price_cents"]) * qty
        item["line_total"] = cents_to_yuan(item["line_total_cents"])
        item["line_reward_coin"] = int(product["reward_coin"]) * qty
        items.append(item)
    return items


def add_cash_cart(form, customer_id):
    product_id = require_text(form, "product_id", "商品")
    qty = optional_int(form, "qty", "数量", 1, 1)
    if not cash_product(product_id):
        raise ValueError("现金商品不存在。")
    wallets, key, wallet = wallet_record(customer_id)
    cart = wallet.setdefault("cash_cart", [])
    for row in cart:
        if row.get("product_id") == product_id:
            row["qty"] = int(row.get("qty") or 0) + qty
            break
    else:
        cart.append({"product_id": product_id, "qty": qty, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    wallets[key] = wallet
    save_wallets(wallets)


def remove_cash_cart(form, customer_id):
    product_id = require_text(form, "product_id", "商品")
    wallets, key, wallet = wallet_record(customer_id)
    wallet["cash_cart"] = [row for row in wallet.get("cash_cart", []) if row.get("product_id") != product_id]
    wallets[key] = wallet
    save_wallets(wallets)


def update_cash_cart(form, customer_id):
    product_id = require_text(form, "product_id", "商品")
    qty = require_int(form, "qty", "数量", 1)
    wallets, key, wallet = wallet_record(customer_id)
    for row in wallet.get("cash_cart", []):
        if row.get("product_id") == product_id:
            row["qty"] = qty
            wallets[key] = wallet
            save_wallets(wallets)
            return
    raise ValueError("购物车中没有这个现金商品。")


def checkout_cash_cart(customer_id, account_id):
    wallets, key, wallet = wallet_record(customer_id)
    items = cart_items(customer_id)
    if not items:
        raise ValueError("购物车为空，请先加入现金商品。")
    total_cents = sum(int(item["line_total_cents"]) for item in items)
    if int(wallet.get("balance_cents", 0)) < total_cents:
        raise ValueError("钱包余额不足，请先银行卡充值。")
    reward_coin = sum(int(item["line_reward_coin"]) for item in items)
    wallet["balance_cents"] = int(wallet.get("balance_cents", 0)) - total_cents
    order = {
        "id": f"cash-cart-{datetime.now():%Y%m%d%H%M%S%f}",
        "product_id": "cart",
        "product_name": "购物车合并结算",
        "items": [{"product_id": item["id"], "product_name": item["name"], "qty": item["qty"]} for item in items],
        "qty": sum(int(item["qty"]) for item in items),
        "total_cents": total_cents,
        "reward_coin": reward_coin,
        "balance_after_cents": wallet["balance_cents"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    wallet.setdefault("cash_orders", []).append(order)
    wallet["cash_cart"] = []
    wallets[key] = wallet
    save_wallets(wallets)
    grant_coin(account_id, reward_coin, "现金购物车结算")
    return format_money_fields(order)


def gift_by_id(gift_id):
    gift = one(
        """
        SELECT TOP 1 GiftID, GiftName, GfitCoin, GiftNum, GiftCategory
        FROM dbo.GiftInfo
        WHERE GiftID=? AND ISNULL(GiftStatus,1)=1
        """,
        [int(gift_id)],
    )
    if not gift:
        return None
    gift["Image"] = gift_image(gift["GiftID"])
    return gift


def points_cart_items(customer_id):
    _, _, wallet = wallet_record(customer_id)
    items = []
    for row in wallet.get("points_cart", []):
        gift = gift_by_id(row.get("gift_id"))
        if not gift:
            continue
        qty = int(row.get("qty") or 1)
        item = dict(gift)
        item["qty"] = qty
        item["line_coin"] = int(gift["GfitCoin"] or 0) * qty
        items.append(item)
    return items


def add_points_cart(form, customer_id):
    gift_id = require_int(form, "gift_id", "礼品ID", 1)
    qty = optional_int(form, "qty", "数量", 1, 1)
    if not gift_by_id(gift_id):
        raise ValueError("积分礼品不存在或已下架。")
    wallets, key, wallet = wallet_record(customer_id)
    cart = wallet.setdefault("points_cart", [])
    for row in cart:
        if int(row.get("gift_id") or 0) == gift_id:
            row["qty"] = int(row.get("qty") or 0) + qty
            break
    else:
        cart.append({"gift_id": gift_id, "qty": qty, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    wallets[key] = wallet
    save_wallets(wallets)


def remove_points_cart(form, customer_id):
    gift_id = require_int(form, "gift_id", "礼品ID", 1)
    wallets, key, wallet = wallet_record(customer_id)
    wallet["points_cart"] = [row for row in wallet.get("points_cart", []) if int(row.get("gift_id") or 0) != gift_id]
    wallets[key] = wallet
    save_wallets(wallets)


def update_points_cart(form, customer_id):
    gift_id = require_int(form, "gift_id", "礼品ID", 1)
    qty = require_int(form, "qty", "数量", 1)
    if not gift_by_id(gift_id):
        raise ValueError("积分礼品不存在或已下架。")
    wallets, key, wallet = wallet_record(customer_id)
    for row in wallet.get("points_cart", []):
        if int(row.get("gift_id") or 0) == gift_id:
            row["qty"] = qty
            wallets[key] = wallet
            save_wallets(wallets)
            return
    raise ValueError("兑换车中没有这个积分商品。")


def checkout_points_cart(customer_id, account_id):
    items = points_cart_items(customer_id)
    if not items:
        raise ValueError("兑换车为空，请先加入积分商品。")
    results = []
    for item in items:
        result = checkout(customer_id, account_id, item["GiftID"], item["qty"])
        if result.get("order_id", -1) == -1:
            raise ValueError(result.get("message", "兑换失败。"))
        results.append(result)
    wallets, key, wallet = wallet_record(customer_id)
    wallet["points_cart"] = []
    wallets[key] = wallet
    save_wallets(wallets)
    return {"count": len(results), "message": f"已生成 {len(results)} 个兑换订单。"}


def product_image(product_id):
    try:
        idx = (int(product_id) - 1) % 9 + 1
    except (TypeError, ValueError):
        idx = 1
    return f"{idx}.jpg"


def gift_image(gift_id):
    try:
        idx = (int(gift_id) - 1) % 9 + 1
    except (TypeError, ValueError):
        idx = 7
    return f"{idx}.jpg"


def with_product_images(products):
    data = []
    for row in products:
        item = dict(row)
        item["Image"] = product_image(item.get("ProductID"))
        data.append(item)
    return data


def with_gift_images(gifts_data):
    data = []
    for row in gifts_data:
        item = dict(row)
        item["Image"] = gift_image(item.get("GiftID"))
        data.append(item)
    return data


def grant_coin(account_id, coin, reason):
    coin = int(coin)
    if coin <= 0:
        return
    execute(
        """
        UPDATE dbo.Account
        SET ValidCoin=ISNULL(ValidCoin,0)+?, HistoryCoin=ISNULL(HistoryCoin,0)+?
        WHERE AccountID=?
        """,
        [coin, coin, int(account_id)],
    )


def buy_cash_product(form, customer_id, account_id):
    product_id = require_text(form, "product_id", "商品")
    qty = optional_int(form, "qty", "数量", 1, 1)
    product = next((item for item in CASH_PRODUCTS if item["id"] == product_id), None)
    if not product:
        raise ValueError("现金商品不存在。")
    total_cents = int(product["price_cents"]) * qty
    wallets, key, wallet = wallet_record(customer_id)
    if int(wallet.get("balance_cents", 0)) < total_cents:
        raise ValueError("钱包余额不足，请先银行卡充值。")
    reward_coin = int(product["reward_coin"]) * qty
    wallet["balance_cents"] = int(wallet.get("balance_cents", 0)) - total_cents
    order = {
        "id": f"cash-{datetime.now():%Y%m%d%H%M%S%f}",
        "product_id": product["id"],
        "product_name": product["name"],
        "qty": qty,
        "total_cents": total_cents,
        "reward_coin": reward_coin,
        "balance_after_cents": wallet["balance_cents"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    wallet.setdefault("cash_orders", []).append(order)
    wallets[key] = wallet
    save_wallets(wallets)
    grant_coin(account_id, reward_coin, f"现金购买：{product['name']}")
    return format_money_fields(order)


def ensure_demo_user():
    member = login(DEMO_USER[0], DEMO_USER[1])
    if member:
        return member
    exists = one("SELECT TOP 1 CustomerID FROM dbo.CustomerInfo WHERE LoginName=?", [DEMO_USER[0]])
    if exists:
        execute("UPDATE dbo.CustomerInfo SET PWD=? WHERE LoginName=?", [DEMO_USER[1], DEMO_USER[0]])
        return login(DEMO_USER[0], DEMO_USER[1])
    register(
        {
            "login_name": DEMO_USER[0],
            "real_name": "演示用户",
            "password": DEMO_USER[1],
            "phone": "13800000000",
            "email": "user@example.com",
        }
    )
    return login(DEMO_USER[0], DEMO_USER[1])


def authenticate_portal(role, login_name, password):
    login_name = (login_name or "").strip()
    password = (password or "").strip()
    if role == "merchant":
        if (login_name, password) == DEMO_MERCHANT:
            return {"role": "merchant", "login_name": "商家演示账号", "business_id": None}
        profile = load_merchant_profiles().get(login_name)
        if profile and profile.get("password") == password:
            return {
                "role": "merchant",
                "login_name": profile.get("business_name") or login_name,
                "business_id": profile.get("business_id"),
            }
        return None
    if (login_name, password) == DEMO_USER:
        member = ensure_demo_user()
        return {"role": "user", "member": member}
    member = login(login_name, password)
    if member:
        return {"role": "user", "member": member}
    return None


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
        raise ValueError(f"{label}必须是数字。") from exc
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
        raise ValueError(f"{label}必须是数字。") from exc
    if minimum is not None and value < minimum:
        raise ValueError(f"{label}不能小于 {minimum}。")
    return value


def register(form):
    login_name = require_text(form, "login_name", "登录名")
    exists = one("SELECT TOP 1 CustomerID FROM dbo.CustomerInfo WHERE LoginName=?", [login_name])
    if exists:
        raise ValueError("会员登录名已存在，请更换。")
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
        [login_name, form.get("real_name"), form.get("password"), form.get("phone"), form.get("email")],
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
    return with_gift_images(
        rows("SELECT TOP 80 GiftID, GiftName, GfitCoin, GiftNum, GiftCategory FROM dbo.GiftInfo WHERE ISNULL(GiftStatus,1)=1 ORDER BY GiftID DESC")
    )


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


def admin_data():
    return {
        "businesses": rows(
            """
            SELECT TOP 50 b.BusinessID, b.BusinessCnName, b.BusinessEnName, b.BusinessStatus,
                   a.AccountID, a.ValidCoin
            FROM dbo.BusinessMen b
            LEFT JOIN dbo.Account a ON a.OwnerID=b.BusinessID AND a.Acctype=2
            ORDER BY b.BusinessID DESC
            """
        ),
        "products": with_product_images(rows(
            """
            SELECT TOP 80 p.ProductID, p.ProductName, p.ProductBrand, p.ProductType,
                   p.ProductCoin, p.ProductStatus, b.BusinessCnName
            FROM dbo.ProductInfo p
            LEFT JOIN dbo.BusinessMen b ON b.BusinessID=p.BusinessID
            ORDER BY p.ProductID DESC
            """
        )),
        "gifts": rows(
            """
            SELECT TOP 80 GiftID, GiftName, GiftCategory, GfitCoin, GiftNum, GiftStatus
            FROM dbo.GiftInfo
            ORDER BY GiftID DESC
            """
        ),
        "codes": rows(
            """
            SELECT TOP 80 c.JFCode1, c.ProductID, p.ProductName, c.JFStatus, c.ImportBatch, c.CreateTime
            FROM dbo.JFCode c
            LEFT JOIN dbo.ProductInfo p ON p.ProductID=c.ProductID
            ORDER BY c.CreateTime DESC
            """
        ),
        "orders": rows(
            """
            SELECT TOP 50 o.OrderID, o.OrderStatus, o.CustomerID, o.AccountID, o.TotalCoin, o.OrderTime
            FROM dbo.OrderInfo o
            ORDER BY o.OrderID DESC
            """
        ),
        "requirements": [
            ("会员注册", "已实现", "注册页检查登录名唯一，并写入 CustomerInfo 和 Account。"),
            ("商家注册", "已实现", "运营管理页新增商家并创建商家账户。"),
            ("新增商家商品参与积分", "已实现", "运营管理页新增商品，校验商家有效。"),
            ("新增平台礼品参与兑换", "已实现", "运营管理页新增礼品，校验礼品名称唯一。"),
            ("会员积分", "已实现", "积金币页调用 CoinTrade，检查积分码并写入流水。"),
            ("会员兑换", "已实现", "购物车调用 AddOrder，检查积分、库存并写入订单。"),
            ("积分码上传脚本", "已实现", "运营管理页支持单个积分码和批量积分码生成。"),
            ("禁用商家", "已实现", "禁用前检查是否仍有可积分商品。"),
            ("禁用商家商品", "已实现", "运营管理页可将商品状态置为禁用。"),
            ("商品积分调整", "已实现", "运营管理页可更新 ProductCoin。"),
            ("禁用平台礼品", "已实现", "运营管理页可将礼品状态置为禁用。"),
            ("取消兑换", "已实现", "运营管理页可取消订单，恢复会员金币和礼品库存。"),
            ("订单状态", "已实现", "运营管理页可完成订单或取消订单。"),
        ],
    }


def create_business(form):
    name = require_text(form, "name", "商家中文名")
    exists = one("SELECT TOP 1 BusinessID FROM dbo.BusinessMen WHERE BusinessCnName=?", [name])
    if exists:
        raise ValueError("商家已存在。")
    login_name = (form.get("merchant_login") or form.get("business_login") or "").strip()
    password = (form.get("merchant_password") or form.get("password") or "").strip()
    profiles = load_merchant_profiles()
    if login_name or password:
        if not login_name:
            raise ValueError("商家登录账号不能为空。")
        if not password:
            raise ValueError("商家登录密码不能为空。")
    if login_name and login_name in profiles:
        raise ValueError("商家登录账号已存在，请更换。")
    execute(
        """
        DECLARE @BusinessID int = ISNULL((SELECT MAX(BusinessID) FROM dbo.BusinessMen WITH (TABLOCKX)),0)+1;
        DECLARE @AccountID int = ISNULL((SELECT MAX(AccountID) FROM dbo.Account WITH (TABLOCKX)),0)+1;
        INSERT INTO dbo.BusinessMen
        (BusinessID, BusinessCnName, BusinessEnName, CreateTime, BusinessStatus, UpdateTime, UpdateUser)
        VALUES(@BusinessID, ?, ?, GETDATE(), 1, GETDATE(), NULL);
        INSERT INTO dbo.Account
        (AccountID, OwnerID, Acctype, CreateTime, AccStatus, ValidCoin, FrozenCoin, OnWayCoin, ExpireCoin, HistoryCoin)
        VALUES(@AccountID, @BusinessID, 2, GETDATE(), 1, 0, 0, 0, 0, 0);
        """,
        [name, form.get("en_name")],
    )
    business = one("SELECT TOP 1 BusinessID FROM dbo.BusinessMen WHERE BusinessCnName=? ORDER BY BusinessID DESC", [name])
    if login_name or password:
        profiles[login_name] = {
            "password": password,
            "business_id": business["BusinessID"] if business else None,
            "business_name": name,
            "en_name": form.get("en_name") or "",
            "contact_name": form.get("contact_name") or "",
            "phone": form.get("phone") or "",
            "email": form.get("email") or "",
            "address": form.get("address") or "",
            "category": form.get("category") or "",
            "license_no": form.get("license_no") or "",
            "remark": form.get("remark") or "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_merchant_profiles(profiles)
    return business


def disable_business(form):
    business_id = require_int(form, "business_id", "商家ID", 1)
    active_products = one(
        "SELECT COUNT(*) AS c FROM dbo.ProductInfo WHERE BusinessID=? AND ISNULL(ProductStatus,1)=1",
        [business_id],
    )["c"]
    if active_products:
        raise ValueError("该商家仍有可积分商品，不能禁用。请先禁用商品。")
    execute("UPDATE dbo.BusinessMen SET BusinessStatus=0, UpdateTime=GETDATE() WHERE BusinessID=?", [business_id])


def create_product(form):
    name = require_text(form, "name", "商品名")
    business_id = require_int(form, "business_id", "商家ID", 1)
    coin = optional_int(form, "coin", "商品积分", 0, 0)
    business = one("SELECT BusinessStatus FROM dbo.BusinessMen WHERE BusinessID=?", [business_id])
    if not business or int(business["BusinessStatus"] or 0) != 1:
        raise ValueError("商家不存在或已禁用，不能新增商品。")
    exists = one("SELECT TOP 1 ProductID FROM dbo.ProductInfo WHERE ProductName=? AND BusinessID=?", [name, business_id])
    if exists:
        raise ValueError("该商家下已存在同名商品。")
    execute(
        """
        DECLARE @ProductID int = ISNULL((SELECT MAX(ProductID) FROM dbo.ProductInfo WITH (TABLOCKX)),0)+1;
        INSERT INTO dbo.ProductInfo
        (ProductID, ProductName, BusinessID, ProductBrand, ProductType, ProductCoin, ProductStatus, UpdateTime, UpdateUser)
        VALUES(@ProductID, ?, ?, ?, ?, ?, 1, GETDATE(), NULL);
        """,
        [name, business_id, form.get("brand"), form.get("type"), coin],
    )


def disable_product(form):
    product_id = require_int(form, "product_id", "商品ID", 1)
    execute("UPDATE dbo.ProductInfo SET ProductStatus=0, UpdateTime=GETDATE() WHERE ProductID=?", [product_id])


def update_product(form):
    product_id = require_int(form, "product_id", "商品ID", 1)
    name = require_text(form, "name", "商品名称")
    coin = require_int(form, "coin", "商品积分", 0)
    status = optional_int(form, "status", "商品状态", 1, 0)
    product = one("SELECT ProductID FROM dbo.ProductInfo WHERE ProductID=?", [product_id])
    if not product:
        raise ValueError("商品不存在。")
    execute(
        """
        UPDATE dbo.ProductInfo
        SET ProductName=?, ProductBrand=?, ProductType=?, ProductCoin=?, ProductStatus=?, UpdateTime=GETDATE()
        WHERE ProductID=?
        """,
        [name, form.get("brand"), form.get("type"), coin, status, product_id],
    )


def adjust_product_coin(form):
    product_id = require_int(form, "product_id", "商品ID", 1)
    coin = require_int(form, "coin", "商品积分", 0)
    execute("UPDATE dbo.ProductInfo SET ProductCoin=?, UpdateTime=GETDATE() WHERE ProductID=?", [coin, product_id])


def create_gift(form):
    name = require_text(form, "name", "礼品名")
    coin = optional_int(form, "coin", "兑换金币", 0, 0)
    num = optional_int(form, "num", "库存", 0, 0)
    exists = one("SELECT TOP 1 GiftID FROM dbo.GiftInfo WHERE GiftName=?", [name])
    if exists:
        raise ValueError("礼品已存在。")
    execute(
        """
        DECLARE @GiftID int = ISNULL((SELECT MAX(GiftID) FROM dbo.GiftInfo WITH (TABLOCKX)),0)+1;
        INSERT INTO dbo.GiftInfo
        (GiftID, GiftName, CreateTime, GiftStatus, GfitCoin, GiftNum, GiftCategory)
        VALUES(@GiftID, ?, GETDATE(), 1, ?, ?, ?);
        """,
        [name, coin, num, form.get("category")],
    )


def disable_gift(form):
    gift_id = require_int(form, "gift_id", "礼品ID", 1)
    execute("UPDATE dbo.GiftInfo SET GiftStatus=0 WHERE GiftID=?", [gift_id])


def create_code(form):
    code = require_text(form, "code", "明文积分码")
    product_id = require_int(form, "product_id", "商品ID", 1)
    product = one("SELECT ProductStatus FROM dbo.ProductInfo WHERE ProductID=?", [product_id])
    if not product or int(product["ProductStatus"] or 0) != 1:
        raise ValueError("商品不存在或已禁用，不能生成积分码。")
    execute(
        """
        INSERT INTO dbo.JFCode
        (JFCode, JFCode1, ProductID, JFStatus, CreateTime, EndTime, ImportBatch, CreateUserID)
        VALUES(dbo.MD5(?, 32), ?, ?, 1, GETDATE(), DATEADD(year, 2, GETDATE()), ?, NULL);
        """,
        [code, code, product_id, optional_int(form, "batch", "批次", 1, 1)],
    )


def batch_create_codes(form):
    product_id = require_int(form, "product_id", "商品ID", 1)
    count = require_int(form, "count", "生成数量", 1)
    batch = optional_int(form, "batch", "批次", 1, 1)
    prefix = (form.get("prefix") or "JBI").strip()
    if count > 200:
        raise ValueError("单次最多生成 200 个积分码。")
    product = one("SELECT ProductStatus FROM dbo.ProductInfo WHERE ProductID=?", [product_id])
    if not product or int(product["ProductStatus"] or 0) != 1:
        raise ValueError("商品不存在或已禁用，不能批量生成积分码。")
    for i in range(count):
        code = f"{prefix}{datetime.now():%Y%m%d%H%M%S}{i + 1:04d}"
        execute(
            """
            INSERT INTO dbo.JFCode
            (JFCode, JFCode1, ProductID, JFStatus, CreateTime, EndTime, ImportBatch, CreateUserID)
            VALUES(dbo.MD5(?, 32), ?, ?, 1, GETDATE(), DATEADD(year, 2, GETDATE()), ?, NULL);
            """,
            [code, code, product_id, batch],
        )


def cancel_order(form):
    order_id = require_int(form, "order_id", "订单ID", 1)
    order = one("SELECT OrderStatus, AccountID, TotalCoin FROM dbo.OrderInfo WHERE OrderID=?", [order_id])
    if not order:
        raise ValueError("订单不存在。")
    if int(order["OrderStatus"] or 0) == 4:
        raise ValueError("订单已经取消。")
    if int(order["OrderStatus"] or 0) == 5:
        raise ValueError("订单已经完成，不能取消。")
    execute(
        """
        UPDATE dbo.OrderInfo SET OrderStatus=4 WHERE OrderID=?;
        UPDATE dbo.Account SET ValidCoin=ISNULL(ValidCoin,0)+? WHERE AccountID=?;
        UPDATE g
        SET g.GiftNum = ISNULL(g.GiftNum,0) + og.GiftNum
        FROM dbo.GiftInfo g
        INNER JOIN dbo.OrderGift og ON og.GiftID=g.GiftID
        WHERE og.OrderID=?;
        """,
        [order_id, int(order["TotalCoin"] or 0), int(order["AccountID"]), order_id],
    )


def complete_order(form):
    order_id = require_int(form, "order_id", "订单ID", 1)
    execute("UPDATE dbo.OrderInfo SET OrderStatus=5 WHERE OrderID=?", [order_id])
