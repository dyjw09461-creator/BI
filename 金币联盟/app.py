from flask import Flask, flash, redirect, render_template, request, session, url_for

from config import Config
from services import mall_service as mall


app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def index():
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
            return redirect(url_for("profile"))
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
    result = None
    if request.method == "POST":
        account_id = request.form.get("account_id") or session.get("account_id")
        result = mall.earn_coin(account_id, request.form.get("code"))
        flash(result.get("message", "处理完成。"), "success" if result.get("result") == 1 else "error")
    return render_template("earn_coin.html", result=result)


@app.route("/cart", methods=["GET", "POST"])
def cart():
    result = None
    gift_rows = mall.gifts()
    if request.method == "POST":
        customer_id = request.form.get("customer_id") or session.get("customer_id")
        account_id = request.form.get("account_id") or session.get("account_id")
        gift_id = request.form.get("gift_id")
        qty = request.form.get("qty") or 1
        if not customer_id or not account_id or not gift_id:
            flash("请先登录或填写会员ID、账户ID，并选择礼品后再结算。", "error")
        else:
            try:
                result = mall.checkout(customer_id, account_id, gift_id, qty)
                flash(result.get("message", "结算完成。"), "success" if result.get("order_id", -1) != -1 else "error")
            except Exception as exc:
                flash(f"结算失败：{exc}", "error")
    return render_template("cart.html", gifts=gift_rows, result=result)


@app.route("/gifts")
def gift_center():
    return render_template("cart.html", gifts=mall.gifts(), result=None, gift_center=True)


@app.route("/profile")
def profile():
    customer_id = request.args.get("customer_id") or session.get("customer_id")
    if not customer_id:
        return redirect(url_for("login"))
    member, orders, trades = mall.profile(customer_id)
    return render_template("profile.html", member=member, orders=orders, trades=trades)


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
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5102, debug=True)
