from flask import Flask, flash, redirect, render_template, request, session, url_for

from config import Config
from services import mall_service as mall


app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def auth_home():
    return render_template("auth.html")


@app.route("/", methods=["POST"])
def auth_submit():
    mode = request.form.get("mode", "login")
    role = request.form.get("role", "user")
    if mode == "merchant_register":
        try:
            business = mall.create_business(request.form)
            session.clear()
            session["role"] = "merchant"
            session["login_name"] = request.form.get("name")
            session["business_id"] = business["BusinessID"] if business else None
            flash("商家注册成功，已进入商家中心。", "success")
            return redirect(url_for("merchant"))
        except Exception as exc:
            flash(str(exc), "error")
            return redirect(url_for("auth_home"))
    if mode == "register":
        try:
            mall.register(request.form)
            member = mall.login(request.form.get("login_name"), request.form.get("password"))
            session["role"] = "user"
            session["customer_id"] = member["CustomerID"]
            session["account_id"] = member["AccountID"]
            session["login_name"] = member["LoginName"]
            flash("注册成功，已进入金币联盟。", "success")
            return redirect(url_for("mall_home"))
        except Exception as exc:
            flash(str(exc), "error")
            return redirect(url_for("auth_home"))
    auth = mall.authenticate_portal(role, request.form.get("login_name"), request.form.get("password"))
    if not auth:
        flash("登录失败，请检查账号和密码。", "error")
        return redirect(url_for("auth_home"))
    session.clear()
    if auth["role"] == "merchant":
        session["role"] = "merchant"
        session["login_name"] = auth["login_name"]
        session["business_id"] = auth.get("business_id")
        flash("商家登录成功。", "success")
        return redirect(url_for("merchant"))
    member = auth["member"]
    session["role"] = "user"
    session["customer_id"] = member["CustomerID"]
    session["account_id"] = member["AccountID"]
    session["login_name"] = member["LoginName"]
    flash("用户登录成功。", "success")
    return redirect(url_for("mall_home"))


@app.route("/mall")
def mall_home():
    if session.get("role") != "user":
        return redirect(url_for("auth_home"))
    return render_template("index.html", **mall.homepage_data())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        member = mall.login(request.form.get("login_name"), request.form.get("password"))
        if member:
            session["customer_id"] = member["CustomerID"]
            session["account_id"] = member["AccountID"]
            session["login_name"] = member["LoginName"]
            flash("登录成功。", "success")
            session["role"] = "user"
            return redirect(url_for("mall_home"))
        flash("登录失败，请检查用户名和密码。", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        mall.register(request.form)
        flash("注册成功，请登录。", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/earn-coin", methods=["GET", "POST"])
def earn_coin():
    if session.get("role") != "user":
        return redirect(url_for("auth_home"))
    result = None
    if request.method == "POST":
        account_id = request.form.get("account_id") or session.get("account_id")
        result = mall.earn_coin(account_id, request.form.get("code"))
        flash(result.get("message", "处理完成。"), "success" if result.get("result") == 1 else "error")
    return render_template("earn_coin.html", result=result)


@app.route("/wallet", methods=["GET", "POST"])
def wallet():
    if session.get("role") != "user":
        return redirect(url_for("auth_home"))
    customer_id = session.get("customer_id")
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "bind_card":
                mall.bind_bank_card(request.form, customer_id)
                flash("银行卡绑定成功。", "success")
            elif action == "recharge":
                result = mall.recharge_wallet(request.form, customer_id)
                flash(f"充值成功，当前余额 {result['balance']} 元。", "success")
            else:
                flash("未知钱包操作。", "error")
        except Exception as exc:
            flash(str(exc), "error")
        return redirect(url_for("wallet"))
    return render_template("wallet.html", wallet=mall.wallet_data(customer_id))


@app.route("/shop", methods=["GET", "POST"])
def shop():
    if session.get("role") != "user":
        return redirect(url_for("auth_home"))
    customer_id = session.get("customer_id")
    account_id = session.get("account_id")
    if request.method == "POST":
        try:
            mall.add_cash_cart(request.form, customer_id)
            flash("商品已加入购物车。", "success")
        except Exception as exc:
            flash(str(exc), "error")
        return redirect(url_for("cart") + "#cash-cart")
    return render_template("shop.html", products=mall.cash_products(), wallet=mall.wallet_data(customer_id))


@app.route("/cart", methods=["GET", "POST"])
def cart():
    if session.get("role") != "user":
        return redirect(url_for("auth_home"))
    result = None
    gift_rows = mall.gifts()
    if request.method == "POST":
        customer_id = session.get("customer_id")
        account_id = session.get("account_id")
        action = request.form.get("action")
        redirect_anchor = "#cash-cart" if "cash" in (action or "") else "#points-cart"
        try:
            if action == "remove_cash_cart":
                mall.remove_cash_cart(request.form, customer_id)
                flash("已从购物车移除。", "success")
            elif action == "update_cash_cart":
                mall.update_cash_cart(request.form, customer_id)
                flash("购物车数量已更新。", "success")
            elif action == "checkout_cash_cart":
                result = mall.checkout_cash_cart(customer_id, account_id)
                flash(f"购物车结算成功，消费 {result['total']} 元，赠送 {result['reward_coin']} 金币。", "success")
            elif action == "remove_points_cart":
                mall.remove_points_cart(request.form, customer_id)
                flash("已从兑换车移除。", "success")
            elif action == "update_points_cart":
                mall.update_points_cart(request.form, customer_id)
                flash("兑换车数量已更新。", "success")
            elif action == "checkout_points_cart":
                result = mall.checkout_points_cart(customer_id, account_id)
                flash(result["message"], "success")
            else:
                flash("未知购物车操作。", "error")
        except Exception as exc:
            flash(f"购物车操作失败：{exc}", "error")
        return redirect(url_for("cart") + redirect_anchor)
    wallet = mall.wallet_data(session.get("customer_id"))
    return render_template("cart.html", wallet=wallet, result=result)


@app.route("/points-mall", methods=["GET", "POST"])
def points_mall():
    if session.get("role") != "user":
        return redirect(url_for("auth_home"))
    result = None
    gift_rows = mall.gifts()
    if request.method == "POST":
        customer_id = session.get("customer_id")
        try:
            mall.add_points_cart(request.form, customer_id)
            flash("积分商品已加入兑换车，请到购物车确认兑换。", "success")
        except Exception as exc:
            flash(str(exc), "error")
        return redirect(url_for("cart") + "#points-cart")
    return render_template("points_mall.html", gifts=gift_rows, result=result, wallet=mall.wallet_data(session.get("customer_id")))


@app.route("/admin-lite", methods=["GET", "POST"])
def admin_lite():
    if session.get("role") != "merchant":
        return redirect(url_for("auth_home"))
    action_map = {
        "create_business": (mall.create_business, "商家已注册，并已创建商家账户。"),
        "disable_business": (mall.disable_business, "商家已禁用。"),
        "create_product": (mall.create_product, "商家商品已新增，可参与积分。"),
        "update_product": (mall.update_product, "商品信息已更新。"),
        "disable_product": (mall.disable_product, "商品已禁用。"),
        "adjust_product_coin": (mall.adjust_product_coin, "商品积分已调整。"),
        "create_gift": (mall.create_gift, "平台礼品已新增，可参与兑换。"),
        "disable_gift": (mall.disable_gift, "礼品已禁用。"),
        "create_code": (mall.create_code, "积分码已生成并加密写入。"),
        "batch_create_codes": (mall.batch_create_codes, "积分码已批量生成。"),
        "cancel_order": (mall.cancel_order, "兑换订单已取消，金币和库存已回补。"),
        "complete_order": (mall.complete_order, "订单状态已设置为完成。"),
    }
    if request.method == "POST":
        action = request.form.get("action")
        handler = action_map.get(action)
        if not handler:
            flash("未知操作。", "error")
        else:
            try:
                handler[0](request.form)
                flash(handler[1], "success")
            except Exception as exc:
                flash(str(exc), "error")
        return redirect(url_for("admin_lite"))
    return render_template("admin_lite.html", **mall.admin_data())


@app.route("/merchant", methods=["GET", "POST"])
def merchant():
    if session.get("role") != "merchant":
        return redirect(url_for("auth_home"))
    action_map = {
        "create_business": (mall.create_business, "商家注册成功，并已创建商家积分账户。"),
        "create_product": (mall.create_product, "商品已新增，可参与积分。"),
        "update_product": (mall.update_product, "商品信息已更新。"),
        "disable_product": (mall.disable_product, "商品已禁用。"),
        "adjust_product_coin": (mall.adjust_product_coin, "商品积分已调整。"),
        "create_code": (mall.create_code, "积分码已生成。"),
        "batch_create_codes": (mall.batch_create_codes, "积分码已批量生成。"),
    }
    if request.method == "POST":
        action = request.form.get("action")
        handler = action_map.get(action)
        if not handler:
            flash("未知商家操作。", "error")
        else:
            try:
                handler[0](request.form)
                flash(handler[1], "success")
            except Exception as exc:
                flash(str(exc), "error")
        return redirect(url_for("merchant"))
    data = mall.admin_data()
    return render_template("merchant.html", businesses=data["businesses"], products=data["products"], codes=data["codes"])


@app.route("/gifts")
def gift_center():
    if session.get("role") != "user":
        return redirect(url_for("auth_home"))
    return redirect(url_for("points_mall"))


@app.route("/profile")
def profile():
    if session.get("role") != "user":
        return redirect(url_for("auth_home"))
    customer_id = request.args.get("customer_id") or session.get("customer_id")
    if not customer_id:
        return redirect(url_for("login"))
    member, orders, trades = mall.profile(customer_id)
    return render_template("profile.html", member=member, orders=orders, trades=trades, wallet=mall.wallet_data(customer_id))


@app.route("/profile/complete")
def profile_complete():
    return render_template("profile_form.html", title="完善个人信息")


@app.route("/profile/edit")
def profile_edit():
    return render_template("profile_form.html", title="修改个人信息")


@app.route("/logout")
def logout():
    session.clear()
    flash("已退出登录。", "success")
    return redirect(url_for("auth_home"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5102, debug=True)
