# -*- coding: big5 -*-
from flask import Flask, render_template, request, redirect, url_for
from crawler_web import get_stock_info  # 匯入你自己寫的爬蟲函式

website_app = Flask(__name__)

# 首頁（查詢欄）
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        stock_code = request.form.get("stock")
        if stock_code:
            return redirect(url_for("stock_page", code=stock_code))
    return render_template("front_page.html")

# 查詢頁
@app.route("/stock/<code>")
def stock_page(code):
    stock_data = get_stock_info(code)
    return render_template("stock.html", summary=stock_data)

# 其他網頁（避免 route 名稱重複）
@app.route("/contact_us")
def contact_us():
    return render_template("contact_us.html")

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/linebot")
def linebot():
    return render_template("linebot.html")

@app.route("/Not_complete")
def not_complete():
    return render_template("Not_complete.html")

if __name__ == "__main__":
    website_app.run(debug=True)
