from flask import render_template,request,redirect,url_for, session, flash
from flask_login import login_user, current_user
from .models import User,Role,Record
from .extensions import db,login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegisterForm
from datetime import datetime

def init_routes(app):

    @app.route("/")
    def home():
        return render_template("home.html")
    
    @app.route("/register", methods = ["POST","GET"])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            
            viewer_role = Role.query.filter_by(name="viewer").first()
            hashed_passwd = generate_password_hash(form.password.data)
            role = Role.query.get(form.role.data)
            user = User(name = form.name.data, email = form.email.data, password = hashed_passwd, role_id = viewer_role.id)
            user.role = role
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        return render_template("register.html", form = form)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route("/login", methods = ["POST","GET"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if not user:
                flash("User not found!", "error")
                return redirect(url_for("login"))
        
            if not check_password_hash(user.password, form.password.data):
                flash("Incorrect password!", "error")
                return redirect(url_for("login"))
            if not user.is_active:
                flash("Account is inactive. Contact admin.", "warning")
                return redirect(url_for("login"))

                
            session["user_id"] = user.id
            session["role"] = user.role.name
            login_user(user)
            flash(f"Welcome back,{user.name} 👋!", "success")
            if user.role.name.lower() == "admin":
                return redirect(url_for("admin_dashboard"))

            elif user.role.name.lower() == "analyst":
                return redirect(url_for("analyst_dashboard"))

            else:
                return redirect(url_for("viewer_dashboard"))
          
        
        return render_template("login.html",form = form)
    

    def role_required(required_role):
        def wrapper(func):
            def decorated(*args, **kwargs):
                if "role" not in session:
                    return redirect(url_for("login"))

                if session["role"] != required_role:
                    flash("Access denied!", "error")
                    return redirect(url_for("home"))

                return func(*args, **kwargs)
            decorated.__name__ = func.__name__
            return decorated
        return wrapper

#-----Dashboard-------#

    @app.route("/viewer")
    @role_required("viewer")
    def viewer_dashboard():
        return render_template("viewer.html")


    @app.route("/analyst")
    @role_required("analyst")
    def analyst_dashboard():
        return render_template("analyst.html")


    @app.route("/admin")
    @role_required("admin")
    def admin_dashboard():

        if not current_user.is_authenticated:
            return redirect(url_for("login"))

        
        return render_template("admin.html")

#--Admin Users--#
    @app.route("/admin/users")
    @role_required("admin")
    def admin_users():
        users = User.query.all()
        return render_template("admin_users.html", users=users)
    
    #--inside admin users--#

    @app.route("/admin/toggle/<int:user_id>")
    @role_required("admin")
    def toggle_user(user_id):
        user = User.query.get(user_id)

        user.is_active = not user.is_active
        db.session.commit()

        return redirect(url_for("admin_users"))

    @app.route("/admin/change_role/<int:user_id>", methods=["POST"])
    @role_required("admin")
    def change_role(user_id):
        user = User.query.get(user_id)

        new_role = request.form["role"]
        role = Role.query.filter_by(name=new_role).first()

        user.role = role
        db.session.commit()

        return redirect(url_for("admin_users"))

    @app.route("/admin/delete_user/<int:user_id>")
    @role_required("admin")
    def delete_user(user_id):
        user = User.query.get(user_id)

        db.session.delete(user)
        db.session.commit()

        return redirect(url_for("admin_users"))
#--Admin Records--#

    @app.route("/admin/records")
    @role_required("admin")
    def view_record():
        records = Record.query.order_by(Record.date.desc()).all()
        return render_template("admin_records.html", records=records)

    @app.route("/add_record", methods=["POST"])
    @role_required("admin")
    def add_record():

        record = Record(
            amount=float(request.form["amount"]),
            type=request.form["type"],
            category=request.form["category"],
            date=datetime.strptime(request.form["date"], "%Y-%m-%d"),
            notes=request.form["notes"],
            user_id=current_user.id
        )

        db.session.add(record)
        db.session.commit()

        flash("Record added!", "success")
        return redirect(url_for("view_record"))
    
    @app.route("/delete/<int:id>",methods = ["POST"])
    @role_required("admin")
    def delete_record(id):
        record = Record.query.get(id)
        db.session.delete(record)
        db.session.commit()
        flash("Deleted!", "success")
        return redirect(url_for("view_record"))

    
    @app.route("/edit/<int:id>", methods=["GET", "POST"])
    @role_required("admin")
    def edit_record(id):
        record = Record.query.get_or_404(id)

        if request.method == "POST":
            record.amount = float(request.form["amount"])
            record.type = request.form["type"]
            record.category = request.form["category"]
            record.date = datetime.strptime(request.form["date"], "%Y-%m-%d")
            record.notes = request.form["notes"]

            db.session.commit()
            flash("Record updated!", "success")
            return redirect(url_for("view_record"))

        return render_template("edit_record.html", record=record)
    
    @app.route("/admin/insights")
    @role_required("admin")
    def admin_insights():
        income_rec = Record.query.filter_by(type = "salary").all()
        tot_in = 0
        tot_exp = 0
        for rec in income_rec:
            tot_in+=rec.amount

        exp_rec = Record.query.filter_by(type = "expense").all()
        for rec in exp_rec:
            tot_exp+=rec.amount

        net_balance = tot_in - tot_exp

        all_records = Record.query.all()  # get everything

        category_totals = {}
        for record in all_records:
            if record.category in category_totals:
                category_totals[record.category] += record.amount
            else:
                category_totals[record.category] = record.amount
        recent_records = Record.query.order_by(Record.date.desc()).limit(10).all()

        monthly_income = {}
        monthly_expense = {}
        for r in all_records:
            month = r.date.strftime("%B")
            if r.type == "income":
                if month not in monthly_income:
                    monthly_income[month] = 0
                monthly_income[month] += r.amount
            elif r.type == "expense":
                if month not in monthly_expense:
                    monthly_expense[month] = 0
                monthly_expense[month] += r.amount
        
        return render_template("admin_insights.html", total_income=tot_in, total_expenses=tot_exp,
        net_balance=net_balance, category_totals=category_totals, recent_records=recent_records, monthly_income=monthly_income,
    monthly_expense=monthly_expense)
    
