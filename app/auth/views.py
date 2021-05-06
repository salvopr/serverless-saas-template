import traceback
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user

from . import auth_blueprint
from app.auth.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from app.user import User
from app.exceptions import UserError, UserDoesNotExists
from app.auth.tokens import create_token, token_user_id


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth_blueprint.links_page"))
    form = LoginForm()
    if form.validate_on_submit():
        user = None
        try:
            user = User(form.email.data)
            user.load()
            if not user.activated:
                flash("User is not activated yet! Check email for an activation link", "danger")
                return redirect(url_for("auth_blueprint.login"))
        except UserDoesNotExists:
            flash("User is not registered", "danger")
            return redirect(url_for("auth_blueprint.login"))
        except UserError:
            print(f"User error in login")
            traceback.print_exc()

        if not user.authenticate(form.password.data):
            flash("Invalid password", "danger")
            return redirect(url_for("auth_blueprint.login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("admin_blueprint.index"))
    return render_template("auth/login.html", form=form)


@auth_blueprint.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    flash("You've been logged out", "success")
    return redirect(url_for("auth_blueprint.login"))


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth_blueprint.login"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(form.email.data)
        user.register(form.password.data)
        token = create_token("REGISTRATION", user.email)
        user.send_registration_email(token)
        flash("Congratulations, you are now a registered user! Check you email for an activation link", "success")
        return redirect(url_for("auth_blueprint.login"))
    return render_template("auth/register.html", form=form)


@auth_blueprint.route("/activate/<token>", methods=["GET"])
def activate(token):
    email = token_user_id(token, "REGISTRATION")
    user = User(email)
    user.activate()
    flash("Congratulations! Your account is activated!", "success")
    return redirect(url_for("auth_blueprint.login"))


@auth_blueprint.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User(form.email.data)
        token = create_token("PASSWORD_RESET", user.email)
        user.send_password_reset_email(token)
        flash("Check you email for a reset link", "success")
    return render_template("auth/forgot_password.html", form=form)


@auth_blueprint.route("/password_reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = token_user_id(token, "PASSWORD_RESET")
        user = User(email)
        user.load()
        user.reset_password(form.password.data)
        flash("Password updated!", "success")
        return redirect(url_for("auth_blueprint.login"))
    return render_template("auth/password_reset.html", form=form)
