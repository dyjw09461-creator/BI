from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from config import Config
from services import bi_service
from services import business_service as svc


app = Flask(__name__)
app.config.from_object(Config)


def handle_form(action, success_message, endpoint):
    try:
        action(request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return None
    except Exception as exc:
        flash(f"操作失败：{exc}", "error")
        return None
    flash(success_message, "success")
    return redirect(url_for(endpoint))


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/bi/kpi")
def api_bi_kpi():
    return jsonify(bi_service.kpi())


@app.route("/api/bi/order-trend")
def api_bi_order_trend():
    return jsonify(bi_service.order_trend())


@app.route("/api/bi/member-trend")
def api_bi_member_trend():
    return jsonify(bi_service.member_trend())


@app.route("/api/bi/gift-ranking")
def api_bi_gift_ranking():
    return jsonify(bi_service.gift_ranking())


@app.route("/api/bi/business-member-ranking")
def api_bi_business_member_ranking():
    return jsonify(bi_service.business_member_ranking())


@app.route("/api/bi/jfcode-status")
def api_bi_jfcode_status():
    return jsonify(bi_service.jfcode_status())


@app.route("/api/bi/area-ranking")
def api_bi_area_ranking():
    return jsonify(bi_service.area_ranking())


@app.route("/api/bi/product-coin-ranking")
def api_bi_product_coin_ranking():
    return jsonify(bi_service.product_coin_ranking())


def list_page(title, endpoint, columns, rows, form_fields=None):
    return render_template(
        "list.html",
        title=title,
        endpoint=endpoint,
        columns=columns,
        rows=rows,
        form_fields=form_fields or [],
        q=request.args.get("q", ""),
    )


@app.route("/customers", methods=["GET", "POST"])
def customers():
    if request.method == "POST":
        response = handle_form(svc.create_customer, "会员已新增，并已创建会员积分账户。", "customers")
        if response:
            return response
    return list_page(
        "会员管理",
        "customers",
        ["CustomerID", "LoginName", "RealName", "Phone", "Email", "AccountID", "ValidCoin"],
        svc.list_customers(request.args.get("q", "")),
        [
            ("login_name", "登录名"),
            ("real_name", "真实姓名"),
            ("password", "密码"),
            ("gender", "性别 1/2"),
            ("phone", "手机号"),
            ("email", "邮箱"),
        ],
    )


@app.route("/businesses", methods=["GET", "POST"])
def businesses():
    if request.method == "POST":
        response = handle_form(svc.create_business, "商家已新增，并已创建商家积分账户。", "businesses")
        if response:
            return response
    return list_page(
        "商家管理",
        "businesses",
        ["BusinessID", "BusinessCnName", "BusinessEnName", "BusinessStatus", "AccountID", "ValidCoin"],
        svc.list_businesses(request.args.get("q", "")),
        [("name", "商家中文名"), ("en_name", "商家英文名")],
    )


@app.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "POST":
        response = handle_form(svc.create_product, "商品已新增。", "products")
        if response:
            return response
    return list_page(
        "商品管理",
        "products",
        ["ProductID", "ProductName", "BusinessCnName", "ProductBrand", "ProductType", "ProductCoin", "ProductStatus"],
        svc.list_products(request.args.get("q", "")),
        [("name", "商品名"), ("business_id", "商家ID"), ("brand", "品牌"), ("type", "类型"), ("coin", "商品积分")],
    )


@app.route("/gifts", methods=["GET", "POST"])
def gifts():
    if request.method == "POST":
        response = handle_form(svc.create_gift, "礼品已新增。", "gifts")
        if response:
            return response
    return list_page(
        "礼品管理",
        "gifts",
        ["GiftID", "GiftName", "GiftCategory", "GfitCoin", "GiftNum", "GiftStatus"],
        svc.list_gifts(request.args.get("q", "")),
        [("name", "礼品名"), ("category", "分类"), ("coin", "兑换金币"), ("num", "库存")],
    )


@app.route("/codes", methods=["GET", "POST"])
def codes():
    if request.method == "POST":
        response = handle_form(svc.create_code, "积分码已新增，MD5 密文已写入。", "codes")
        if response:
            return response
    return list_page(
        "积分码管理",
        "codes",
        ["JFCode1", "ProductID", "ProductName", "JFStatus", "CreateTime", "EndTime", "ImportBatch"],
        svc.list_codes(request.args.get("q", "")),
        [("code", "明文积分码"), ("product_id", "商品ID"), ("batch", "批次")],
    )


@app.route("/earn", methods=["GET", "POST"])
def earn():
    result = None
    if request.method == "POST":
        result = svc.earn_coin(request.form.get("account_id"), request.form.get("code"))
        flash(result.get("message", "积分处理完成。"), "success" if result.get("result") == 1 else "error")
    return render_template("action.html", title="积分获取", result=result, fields=[("account_id", "会员账户ID"), ("code", "明文积分码")])


@app.route("/exchange", methods=["GET", "POST"])
def exchange():
    result = None
    if request.method == "POST":
        result = svc.exchange_gift(
            request.form.get("customer_id"),
            request.form.get("account_id"),
            request.form.get("gift_id"),
            request.form.get("gift_num"),
        )
        flash(result.get("message", "兑换处理完成。"), "success" if result.get("order_id", -1) != -1 else "error")
    return render_template(
        "action.html",
        title="礼品兑换",
        result=result,
        fields=[("customer_id", "会员ID"), ("account_id", "会员账户ID"), ("gift_id", "礼品ID"), ("gift_num", "数量")],
    )


@app.route("/orders")
def orders():
    return list_page(
        "订单管理",
        "orders",
        ["OrderID", "OrderTime", "OrderStatus", "CustomerID", "LoginName", "TotalCoin", "GiftLines"],
        svc.list_orders(),
    )


@app.route("/trades")
def trades():
    return list_page(
        "积分流水",
        "trades",
        ["TradeLogID", "TradeTime", "JFCode", "ProductID", "BusinessID", "TradeType", "OrderID", "Coin", "AccountID"],
        svc.list_trades(),
    )


@app.route("/seed")
def seed():
    return render_template("seed.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5101, debug=True)
