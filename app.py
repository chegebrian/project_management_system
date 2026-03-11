# Standard library imports
from datetime import date, datetime  # used for handling dates (e.g., move-in dates, payment dates)

# Flask core imports
from flask import (
    Flask,              # main Flask class to create the app
    current_app,        # proxy to the current app context
    flash,              # display one-time messages to the user
    jsonify,            # return JSON responses
    redirect,           # redirect the user to a different route
    render_template,    # render Jinja2 templates
    request,            # access HTTP request data
    url_for              # generate URLs for routes
)

# Flask-Login imports
from flask_login import (
    LoginManager,       # manage user session and authentication
    current_user,       # proxy for the currently logged-in user
    login_required,     # decorator to protect routes
    login_user,         # log a user in
    logout_user         # log a user out
)

# Flask-WTF import
from flask_wtf.csrf import CSRFProtect  # enable CSRF protection for forms

# SQLAlchemy import
from sqlalchemy import text  # for executing raw SQL statements

# Project-specific configuration
from config import Config  # import app configuration (e.g., SECRET_KEY, database URI)

# Forms used in the app
from forms import (
    LoginForm,           # form for user login
    PaymentForm,         # form for recording payments
    PropertyForm,        # form for creating/updating properties
    RegistrationForm,    # form for registering new users
    TenantForm,          # form for creating/updating tenants
    UnitForm,            # form for creating/updating units
)

# Database models
from models import (
    Payment,             # model representing tenant payments
    Property,            # model representing real estate properties
    Tenant,              # model representing tenants
    Unit,                # model representing units in properties
    User,                # model representing application users
    db                   # SQLAlchemy database instance
)

login_manager = LoginManager()
login_manager.login_view = "login"

def _ensure_sqlite_schema() -> None:
    """
    Minimal SQLite schema sync for simple deployments (no Alembic).
    Adds newly introduced columns that `db.create_all()` will not backfill.
    """
    engine = db.get_engine()
    if engine.dialect.name != "sqlite":
        return

    # `payment_status` was introduced after some DBs were already created.
    try:
        cols = db.session.execute(text("PRAGMA table_info(payment)")).fetchall()
    except Exception:
        # Table may not exist yet (fresh DB); `create_all()` handles that.
        return

    col_names = {row[1] for row in cols}  # PRAGMA: (cid, name, type, notnull, dflt_value, pk)

    # NOTE: SQLite's ALTER TABLE is limited; we can add columns but not add
    # UNIQUE constraints retroactively. For MVP/dev DBs this is acceptable.
    alters: list[str] = []
    if "payment_status" not in col_names:
        alters.append(
            "ALTER TABLE payment ADD COLUMN payment_status VARCHAR(20) DEFAULT 'completed'"
        )
    if "mpesa_checkout_request_id" not in col_names:
        alters.append("ALTER TABLE payment ADD COLUMN mpesa_checkout_request_id VARCHAR(50)")
    if "mpesa_receipt_number" not in col_names:
        alters.append("ALTER TABLE payment ADD COLUMN mpesa_receipt_number VARCHAR(50)")
    if "mpesa_phone" not in col_names:
        alters.append("ALTER TABLE payment ADD COLUMN mpesa_phone VARCHAR(20)")

    for stmt in alters:
        db.session.execute(text(stmt))
    if alters:
        db.session.commit()


def _ensure_all_property_units() -> None:
    """Create missing units for all existing properties so Unit dropdowns (Tenants, Payments) are populated."""
    for prop in Property.query.all():
        existing_count = Unit.query.filter_by(property_id=prop.id).count()
        to_add = max(0, prop.num_units - existing_count)
        for i in range(to_add):
            unit = Unit(
                name=f"Unit {existing_count + i + 1}",
                property=prop,
                is_occupied=False,
            )
            db.session.add(unit)
    db.session.commit()

def _sync_unit_occupancy_from_tenants() -> None:
    """
    Keep Unit.is_occupied consistent with tenant assignment.
    A unit is considered occupied if it has an active tenant.
    """
    units = Unit.query.all()
    changed = False
    for u in units:
        has_active_tenant = bool(u.tenant and u.tenant.active)
        if u.is_occupied != has_active_tenant:
            u.is_occupied = has_active_tenant
            changed = True
    if changed:
        db.session.commit()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    register_routes(app)

    with app.app_context():
        db.create_all()
        _ensure_sqlite_schema()
        _ensure_all_property_units()
        _sync_unit_occupancy_from_tenants()

    # M-Pesa callback is called by Safaricom; must be CSRF-exempt
    if "mpesa_callback" in app.view_functions:
        csrf.exempt(app.view_functions["mpesa_callback"])

    return app


def register_routes(app: Flask) -> None:
    @app.route("/")
    @app.route("/dashboard")
    @login_required
    def dashboard():
        total_properties = Property.query.count()
        total_tenants = Tenant.query.count()
        total_units = Unit.query.count()
        occupied_units = Unit.query.filter_by(is_occupied=True).count()
        vacant_units = total_units - occupied_units

        today = date.today()
        monthly_rent_collected = (
            db.session.query(db.func.coalesce(db.func.sum(Payment.amount), 0.0))
            .filter(Payment.month == today.month, Payment.year == today.year)
            .scalar()
        )

        expected_rent = 0.0
        occupied = Unit.query.filter_by(is_occupied=True).all()
        for unit in occupied:
            expected_rent += unit.property.rent_price
        unpaid_rent = max(expected_rent - monthly_rent_collected, 0.0)

        return render_template(
            "dashboard.html",
            total_properties=total_properties,
            total_tenants=total_tenants,
            occupied_units=occupied_units,
            vacant_units=vacant_units,
            monthly_rent_collected=monthly_rent_collected,
            unpaid_rent=unpaid_rent,
        )

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        form = RegistrationForm()
        if form.validate_on_submit():
            if User.query.filter(
                (User.username == form.username.data) | (User.email == form.email.data)
            ).first():
                flash("Username or email already taken.", "danger")
                return redirect(url_for("register"))
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash("Invalid username or password.", "danger")
                return redirect(url_for("login"))
            login_user(user, remember=form.remember_me.data)
            flash("Logged in successfully.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/properties")
    @login_required
    def list_properties():
        properties = Property.query.all()
        return render_template("properties.html", properties=properties)

    def _ensure_property_units(prop: Property, target_count: int) -> None:
        """Create placeholder units (Unit 1, Unit 2, ...) so property has target_count units."""
        existing = Unit.query.filter_by(property_id=prop.id).count()
        to_add = max(0, target_count - existing)
        for i in range(to_add):
            unit = Unit(
                name=f"Unit {existing + i + 1}",
                property=prop,
                is_occupied=False,
            )
            db.session.add(unit)

    @app.route("/properties/add", methods=["GET", "POST"])
    @login_required
    def add_property():
        form = PropertyForm()
        if form.validate_on_submit():
            prop = Property(
                name=form.name.data,
                location=form.location.data,
                property_type=form.property_type.data,
                num_units=form.num_units.data,
                rent_price=form.rent_price.data,
            )
            db.session.add(prop)
            db.session.commit()
            _ensure_property_units(prop, form.num_units.data)
            db.session.commit()
            flash("Property created.", "success")
            return redirect(url_for("list_properties"))
        return render_template("property_form.html", form=form, title="Add Property")

    @app.route("/properties/<int:property_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_property(property_id: int):
        prop = Property.query.get_or_404(property_id)
        form = PropertyForm(obj=prop)
        if form.validate_on_submit():
            prop.name = form.name.data
            prop.location = form.location.data
            prop.property_type = form.property_type.data
            prop.num_units = form.num_units.data
            prop.rent_price = form.rent_price.data
            db.session.commit()
            _ensure_property_units(prop, form.num_units.data)
            db.session.commit()
            flash("Property updated.", "success")
            return redirect(url_for("list_properties"))
        return render_template("property_form.html", form=form, title="Edit Property")

    @app.route("/properties/<int:property_id>/delete", methods=["POST"])
    @login_required
    def delete_property(property_id: int):
        prop = Property.query.get_or_404(property_id)
        db.session.delete(prop)
        db.session.commit()
        flash("Property deleted.", "info")
        return redirect(url_for("list_properties"))

    @app.route("/properties/<int:property_id>")
    @login_required
    def property_detail(property_id: int):
        prop = Property.query.get_or_404(property_id)
        units = Unit.query.filter_by(property_id=property_id).all()
        return render_template("property_detail.html", property=prop, units=units)

    @app.route("/properties/<int:property_id>/units/add", methods=["GET", "POST"])
    @login_required
    def add_unit(property_id: int):
        prop = Property.query.get_or_404(property_id)
        form = UnitForm()
        if form.validate_on_submit():
            unit = Unit(
                name=form.name.data,
                is_occupied=form.is_occupied.data,
                property=prop,
            )
            db.session.add(unit)
            db.session.commit()
            flash("Unit created.", "success")
            return redirect(url_for("property_detail", property_id=property_id))
        return render_template("unit_form.html", form=form, property=prop, title="Add Unit")

    @app.route("/units/<int:unit_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_unit(unit_id: int):
        unit = Unit.query.get_or_404(unit_id)
        form = UnitForm(obj=unit)
        if form.validate_on_submit():
            unit.name = form.name.data
            unit.is_occupied = form.is_occupied.data
            db.session.commit()
            flash("Unit updated.", "success")
            return redirect(url_for("property_detail", property_id=unit.property_id))
        return render_template("unit_form.html", form=form, property=unit.property, title="Edit Unit")

    @app.route("/units/<int:unit_id>/delete", methods=["POST"])
    @login_required
    def delete_unit(unit_id: int):
        unit = Unit.query.get_or_404(unit_id)
        property_id = unit.property_id
        db.session.delete(unit)
        db.session.commit()
        flash("Unit deleted.", "info")
        return redirect(url_for("property_detail", property_id=property_id))

    @app.route("/tenants")
    @login_required
    def list_tenants():
        tenants = Tenant.query.all()
        return render_template("tenants.html", tenants=tenants)

    def _populate_tenant_unit_choices(form: TenantForm) -> None:
        units = Unit.query.order_by(Unit.property_id, Unit.name).all()
        choices = [(0, "Unassigned")]
        for u in units:
            label = f"{u.property.name} - {u.name}"
            choices.append((u.id, label))
        form.unit_id.choices = choices

    @app.route("/tenants/add", methods=["GET", "POST"])
    @login_required
    def add_tenant():
        form = TenantForm()
        _populate_tenant_unit_choices(form)
        if form.validate_on_submit():
            unit = Unit.query.get(form.unit_id.data) if form.unit_id.data else None
            tenant = Tenant(
                full_name=form.full_name.data,
                email=form.email.data,
                phone=form.phone.data,
                move_in_date=form.move_in_date.data or date.today(),
                active=form.active.data,
                unit=unit,
            )
            if unit and not unit.is_occupied:
                unit.is_occupied = True
            db.session.add(tenant)
            db.session.commit()
            flash("Tenant created.", "success")
            return redirect(url_for("list_tenants"))
        return render_template("tenant_form.html", form=form, title="Add Tenant")

    @app.route("/tenants/<int:tenant_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_tenant(tenant_id: int):
        tenant = Tenant.query.get_or_404(tenant_id)
        form = TenantForm(obj=tenant)
        _populate_tenant_unit_choices(form)
        current_unit_id = tenant.unit_id or 0
        form.unit_id.data = current_unit_id

        if form.validate_on_submit():
            new_unit_id = form.unit_id.data or 0
            if new_unit_id != current_unit_id:
                if tenant.unit:
                    tenant.unit.is_occupied = False
                if new_unit_id:
                    new_unit = Unit.query.get(new_unit_id)
                    tenant.unit = new_unit
                    new_unit.is_occupied = True
                else:
                    tenant.unit = None

            tenant.full_name = form.full_name.data
            tenant.email = form.email.data
            tenant.phone = form.phone.data
            tenant.move_in_date = form.move_in_date.data or tenant.move_in_date
            tenant.active = form.active.data
            db.session.commit()
            flash("Tenant updated.", "success")
            return redirect(url_for("list_tenants"))
        return render_template("tenant_form.html", form=form, title="Edit Tenant")

    @app.route("/tenants/<int:tenant_id>/delete", methods=["POST"])
    @login_required
    def delete_tenant(tenant_id: int):
        tenant = Tenant.query.get_or_404(tenant_id)
        if tenant.unit:
            tenant.unit.is_occupied = False
        db.session.delete(tenant)
        db.session.commit()
        flash("Tenant removed.", "info")
        return redirect(url_for("list_tenants"))


    @app.route("/payments", methods=["GET", "POST"])
    @login_required
    def payments():
        form = PaymentForm()

        # Populate tenant choices with active tenants
        tenants = Tenant.query.filter_by(active=True).all()
        form.tenant_id.choices = [(t.id, t.full_name) for t in tenants]

        # Populate unit choices (ordered by property and unit name)
        units = Unit.query.order_by(Unit.property_id, Unit.name).all()
        form.unit_id.choices = [(u.id, f"{u.property.name} - {u.name}") for u in units]

        if form.validate_on_submit():
            tenant = Tenant.query.get_or_404(form.tenant_id.data)
            unit = Unit.query.get_or_404(form.unit_id.data)

            # Link tenant to unit if not already linked
            if tenant.unit_id != unit.id:
                if tenant.unit:
                    tenant.unit.is_occupied = False
                tenant.unit = unit
                unit.is_occupied = True

            # Record the payment
            payment = Payment(
                tenant=tenant,
                unit=unit,
                property=unit.property,
                amount=form.amount.data,
                month=form.month.data,
                year=form.year.data,
                payment_date=datetime.utcnow(),
            )
            db.session.add(payment)
            db.session.commit()
            flash("Payment recorded.", "success")
            return redirect(url_for("payments"))

        # Get latest 100 payments for display
        all_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(100).all()

        return render_template(
            "payments.html",
            form=form,
            payments=all_payments,
        )

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
