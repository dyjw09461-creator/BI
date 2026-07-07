from config import Config
from db.sqlserver import one, rows


def kpi():
    return one("SELECT TOP 1 * FROM dbo.vw_dashboard_kpi", database=Config.DW_DATABASE) or {}


def order_trend():
    return rows("SELECT * FROM dbo.vw_dashboard_order_trend ORDER BY DateKey", database=Config.DW_DATABASE)


def member_trend():
    return rows("SELECT * FROM dbo.vw_dashboard_member_trend ORDER BY DateKey", database=Config.DW_DATABASE)


def gift_ranking():
    return rows(
        "SELECT TOP 10 * FROM dbo.vw_dashboard_gift_ranking ORDER BY ExchangeCoin DESC",
        database=Config.DW_DATABASE,
    )


def business_member_ranking():
    return rows(
        "SELECT TOP 10 * FROM dbo.vw_dashboard_business_member_ranking ORDER BY MemberCount DESC",
        database=Config.DW_DATABASE,
    )


def jfcode_status():
    return rows("SELECT * FROM dbo.vw_dashboard_jfcode_status ORDER BY JFStatus", database=Config.DW_DATABASE)


def area_ranking():
    return rows(
        "SELECT TOP 10 * FROM dbo.vw_dashboard_area_ranking ORDER BY MemberCount DESC, OrderCount DESC",
        database=Config.DW_DATABASE,
    )


def product_coin_ranking():
    return rows(
        "SELECT TOP 10 * FROM dbo.vw_dashboard_product_coin_ranking ORDER BY UsedCoin DESC",
        database=Config.DW_DATABASE,
    )
