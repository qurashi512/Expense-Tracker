from flask import Flask, render_template, request, session, redirect, flash
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# ==================== إعداد التطبيق ====================

app = Flask(__name__)

# إعداد الـ Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ربط قاعدة البيانات
db = SQL("sqlite:///finance.db")


# ==================== إنشاء الجداول ====================
# شغّل ده مرة واحدة عند بداية المشروع

# CREATE TABLE users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT NOT NULL UNIQUE,
#     hash TEXT NOT NULL
# );

# CREATE TABLE expenses (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER NOT NULL,
#     amount REAL NOT NULL,
#     category TEXT NOT NULL,
#     note TEXT,
#     date TEXT NOT NULL,
#     FOREIGN KEY(user_id) REFERENCES users(id)
# );

# CREATE TABLE budgets (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER NOT NULL,
#     month TEXT NOT NULL,
#     income REAL DEFAULT 0,
#     limit_amount REAL DEFAULT 0,
#     FOREIGN KEY(user_id) REFERENCES users(id)
# );


# ==================== Login Required Decorator ====================

def login_required(f):
    """يتأكد إن المستخدم logged in قبل ما يدخل أي صفحة محمية"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# ==================== صفحة الـ Dashboard (الرئيسية) ====================

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]

    # إجمالي مصروفات الشهر الحالي
    total_result = db.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = ?
        AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """, user_id)
    total = total_result[0]["total"]

    # آخر 5 مصروفات
    recent = db.execute("""
        SELECT * FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT 5
    """, user_id)

    # بيانات الميزانية للشهر الحالي
    budget_data = db.execute("""
        SELECT * FROM budgets
        WHERE user_id = ?
        AND month = strftime('%Y-%m', 'now')
    """, user_id)
    budget = budget_data[0] if budget_data else None

    # حساب المتبقي
    remaining = None
    if budget and budget["income"] > 0:
        remaining = budget["income"] - total

    # تحذير لو وصل 90% من الحد الأقصى
    warning = False
    if budget and budget["limit_amount"] > 0:
        warning = total >= (budget["limit_amount"] * 0.9)

    # بيانات الـ Chart (مصروفات الشهر مصنّفة)
    categories = db.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        WHERE user_id = ?
        AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        GROUP BY category
        ORDER BY total DESC
    """, user_id)

    return render_template("index.html",
                           total=total,
                           recent=recent,
                           budget=budget,
                           remaining=remaining,
                           warning=warning,
                           categories=categories)


# ==================== إضافة مصروف ====================

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        amount   = request.form.get("amount")
        category = request.form.get("category")
        note     = request.form.get("note")
        date     = request.form.get("date")

        # التحقق من الإدخال
        if not amount or not category or not date:
            flash("Please fill in all required fields.", "danger")
            return render_template("add.html")
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number.", "danger")
            return render_template("add.html")

        db.execute("""
            INSERT INTO expenses (user_id, amount, category, note, date)
            VALUES (?, ?, ?, ?, ?)
        """, session["user_id"], amount, category, note, date)

        flash("Expense added successfully! ✅", "success")
        return redirect("/")

    return render_template("add.html")


# ==================== سجل المصروفات ====================

@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]

    # فلترة اختيارية بالكاتيجوري
    category_filter = request.args.get("category", "")

    if category_filter:
        expenses = db.execute("""
            SELECT * FROM expenses
            WHERE user_id = ? AND category = ?
            ORDER BY date DESC
        """, user_id, category_filter)
    else:
        expenses = db.execute("""
            SELECT * FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC
        """, user_id)

    # قائمة الكاتيجوريز المتاحة للفلتر
    all_categories = db.execute("""
        SELECT DISTINCT category FROM expenses
        WHERE user_id = ?
        ORDER BY category
    """, user_id)

    return render_template("history.html",
                           expenses=expenses,
                           all_categories=all_categories,
                           selected_category=category_filter)


# ==================== تعديل مصروف ====================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    user_id = session["user_id"]

    # التأكد إن المصروف ده بتاع الـ user الحالي فقط
    expense = db.execute("""
        SELECT * FROM expenses
        WHERE id = ? AND user_id = ?
    """, id, user_id)

    if not expense:
        flash("Expense not found.", "danger")
        return redirect("/history")

    expense = expense[0]

    if request.method == "POST":
        amount   = request.form.get("amount")
        category = request.form.get("category")
        note     = request.form.get("note")
        date     = request.form.get("date")

        # التحقق من الإدخال
        if not amount or not category or not date:
            flash("Please fill in all required fields.", "danger")
            return render_template("edit.html", expense=expense)

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number.", "danger")
            return render_template("edit.html", expense=expense)

        db.execute("""
            UPDATE expenses
            SET amount = ?, category = ?, note = ?, date = ?
            WHERE id = ? AND user_id = ?
        """, amount, category, note, date, id, user_id)

        flash("Expense updated successfully! ✏️", "success")
        return redirect("/history")

    return render_template("edit.html", expense=expense)


# ==================== حذف مصروف ====================

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    user_id = session["user_id"]

    # التأكد إن المصروف بتاع الـ user الحالي فقط
    expense = db.execute("""
        SELECT * FROM expenses
        WHERE id = ? AND user_id = ?
    """, id, user_id)

    if not expense:
        flash("Expense not found.", "danger")
        return redirect("/history")

    db.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", id, user_id)

    flash("Expense deleted. 🗑️", "success")
    return redirect("/history")


# ==================== الميزانية ====================

@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    user_id = session["user_id"]

    if request.method == "POST":
        income = request.form.get("income")
        limit  = request.form.get("limit")
        month  = request.form.get("month")
        if not income or not month:
            flash("Please fill in income and month.", "danger")
            return render_template("budget.html")

        try:
            income = float(income)
            limit  = float(limit) if limit else 0
        except ValueError:
            flash("Please enter valid numbers.", "danger")
            return render_template("budget.html")

        # لو موجود — update، لو لأ — insert
        existing = db.execute("""
            SELECT id FROM budgets
            WHERE user_id = ? AND month = ?
        """, user_id, month)

        if existing:
            db.execute("""
                UPDATE budgets
                SET income = ?, limit_amount = ?
                WHERE user_id = ? AND month = ?
            """, income, limit, user_id, month)
        else:
            db.execute("""
                INSERT INTO budgets (user_id, month, income, limit_amount)
                VALUES (?, ?, ?, ?)
            """, user_id, month, income, limit)

        flash("Budget saved! 💰", "success")
        return redirect("/")

    # جيب الميزانية الحالية لو موجودة
    current_budget = db.execute("""
        SELECT * FROM budgets
        WHERE user_id = ?
        AND month = strftime('%Y-%m', 'now')
    """, user_id)
    current_budget = current_budget[0] if current_budget else None

    return render_template("budget.html", current_budget=current_budget)


# ==================== التقارير ====================

@app.route("/reports")
@login_required
def reports():
    user_id = session["user_id"]

    # مصروفات كل شهر (آخر 6 شهور)
    monthly = db.execute("""
        SELECT strftime('%Y-%m', date) AS month,
               SUM(amount) AS total
        FROM expenses
        WHERE user_id = ?
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    """, user_id)

    # مصروفات كل كاتيجوري (الشهر الحالي)
    by_category = db.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        WHERE user_id = ?
        AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
        GROUP BY category
        ORDER BY total DESC
    """, user_id)

    # إجمالي كل الوقت
    all_time = db.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = ?
    """, user_id)[0]["total"]

    return render_template("reports.html",
                           monthly=monthly,
                           by_category=by_category,
                           all_time=all_time)


# ==================== تسجيل الدخول ====================

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please enter username and password.", "danger")
            return render_template("login.html")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        flash(f"Welcome back, {username}! 👋", "success")
        return redirect("/")

    return render_template("login.html")


# ==================== إنشاء حساب ====================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username        = request.form.get("username")
        password        = request.form.get("password")
        confirm         = request.form.get("confirmation")

        if not username or not password or not confirm:
            flash("Please fill in all fields.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        # التأكد إن الـ username مش موجود
        existing = db.execute("SELECT id FROM users WHERE username = ?", username)
        if existing:
            flash("Username already taken.", "danger")
            return render_template("register.html")

        # حفظ الـ password كـ hash
        hashed = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed)

        # تسجيل دخول تلقائي بعد التسجيل
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]
        session["username"] = username

        flash(f"Account created! Welcome, {username}! 🎉", "success")
        return redirect("/")

    return render_template("register.html")


# ==================== تسجيل الخروج ====================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ==================== تشغيل التطبيق ====================

if __name__ == "__main__":
    app.run(debug=True)
