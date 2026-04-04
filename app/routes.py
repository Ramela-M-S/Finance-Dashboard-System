
from flask import render_template,request,redirect,url_for, session, flash
from flask_login import login_user, current_user
from .models import User,Role,Record
from .extensions import db,login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegisterForm
from datetime import datetime
from collections import OrderedDict
from datetime import datetime

def init_routes(app):

    @app.route("/")
    def home():
        return render_template("base.html")
    
    @app.route("/register", methods = ["POST","GET"])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            
            viewer_role = Role.query.filter_by(name="viewer").first()
            hashed_passwd = generate_password_hash(form.password.data)
           
            user = User(name = form.name.data, email = form.email.data, password = hashed_passwd, role_id = viewer_role.id)
            
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
    

    def role_required(*allowed_roles):
        def wrapper(func):
            def decorated(*args, **kwargs):
                if "role" not in session:
                    return redirect(url_for("login"))

                if session["role"] not in allowed_roles:
                    flash("Access denied!", "error")
                    return redirect(url_for("home"))

                return func(*args, **kwargs)
            decorated.__name__ = func.__name__
            return decorated
        return wrapper

#-----Dashboard-------#

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
        users = User.query.all()
        records = Record.query.order_by(Record.date.desc()).all()
        return render_template("admin_records.html", records=records, users = users)

    @app.route("/add_record", methods=["POST"])
    @role_required("admin")
    def add_record():
        users = User.query.filter(User.role_id != current_user.role_id).all()

        record = Record(
            amount=float(request.form["amount"]),
            type=request.form["type"],
            category=request.form["category"],
            date=datetime.strptime(request.form["date"], "%Y-%m-%d"),
            notes=request.form["notes"],
            user_id=int(request.form["user_id"])
        )

        db.session.add(record)
        db.session.commit()

        flash("Record added successfully!", "success")
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
    @role_required("admin","analyst")
    def admin_insights():
    # Calculate total income
        income_rec = Record.query.filter_by(type="income").all()
        tot_in = sum(rec.amount for rec in income_rec)

        # Calculate total expenses
        exp_rec = Record.query.filter_by(type="expense").all()
        tot_exp = sum(rec.amount for rec in exp_rec)

        # Net balance
        net_balance = tot_in - tot_exp

        # All records for other calculations
        all_records = Record.query.all()

        # Category-wise totals
        category_totals = {}
        for record in all_records:
            category_totals[record.category] = category_totals.get(record.category, 0) + record.amount

        # Recent transactions
        recent_records = Record.query.order_by(Record.date.desc()).limit(10).all()

        # Monthly trends
        months = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]
        monthly_income = OrderedDict((m, 0) for m in months)
        monthly_expense = OrderedDict((m, 0) for m in months)
        for r in all_records:
            month = r.date.strftime("%B")
            r_type = r.type.lower()  # abbreviated month to match keys
            if r_type == "income":
                if month not in monthly_income:
                    monthly_income[month] = 0
                monthly_income[month] += r.amount
            elif r_type == "expense":
                if month not in monthly_income:
                    monthly_expense[month] = 0
                monthly_expense[month] += r.amount
        print("Monthly exepenses:",monthly_expense)
        print("Monthly income:",monthly_income)
        return render_template(
            "admin_insights.html", 
            total_income=tot_in, 
            total_expenses=tot_exp,
            net_balance=net_balance, 
            category_totals=category_totals, 
            recent_records=recent_records, 
            monthly_income=monthly_income,
            monthly_expense=monthly_expense
        )
    
    #---Filter & Search---#
    @app.route("/admin/filter", methods=["GET", "POST"])
    @role_required("admin","analyst")
    def admin_filter():
        # initial values
        records = Record.query.order_by(Record.date.desc()).all()
        categories = [c[0] for c in db.session.query(Record.category).distinct()]

        selected_type = "all"
        selected_category = "all"
        start_date = ""
        end_date = ""

        if request.method == "POST":
            selected_type = request.form.get("type", "all")
            selected_category = request.form.get("category", "all")
            start_date = request.form.get("start_date", "")
            end_date = request.form.get("end_date", "")

            query = Record.query

            if selected_type != "all":
                query = query.filter_by(type=selected_type)

            if selected_category != "all":
                query = query.filter_by(category=selected_category)

            if start_date:
                query = query.filter(Record.date >= start_date)

            if end_date:
                query = query.filter(Record.date <= end_date)

            records = query.order_by(Record.date.desc()).all()

        return render_template(
            "admin_filter.html",
            records=records,
            categories=categories,
            selected_type=selected_type,
            selected_category=selected_category,
            start_date=start_date,
            end_date=end_date
        )
    

#---Analyst---#

    @app.route("/analyst")
    @role_required("analyst")
    def analyst_dashboard():

        if not current_user.is_authenticated:
            return redirect(url_for("login"))

        
        return render_template("analyst.html")

#---Viewer---#

    @app.route("/viewer")
    @role_required("viewer")
    def viewer_dashboard():
        user_id = session["user_id"]
        records = Record.query.filter_by(user_id=user_id).all()
        total_income = 0
        total_expense = 0

        for r in records:
            if r.type == "income":
                total_income += r.amount
            else:
                total_expense += r.amount
        balance = total_income - total_expense
        return render_template(
            "viewer.html",
            records=records,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance
        )
        

