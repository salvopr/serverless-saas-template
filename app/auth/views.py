from flask import render_template, redirect, url_for, flash, current_app
from flask_login import current_user, login_user, logout_user

from . import auth_blueprint
from app.auth.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from app.user import User
from app.exceptions import UserDoesNotExists
from app.auth.tokens import create_token, token_user_id
from app.events import new_event, EventTypes


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("platform_blueprint.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = None
        try:
            user = User(form.email.data)
            user.load()
            if not user.activated:
                flash("User is not activated yet! Check email for an activation link", "danger")
                current_app.logger.warning(f'User {form.email.data} not activated')
                return redirect(url_for("auth_blueprint.login"))
        except UserDoesNotExists:
            flash("User is not registered", "danger")
            current_app.logger.warning(f'No such user {form.email.data}')
            return redirect(url_for("auth_blueprint.login"))

        if not user.authenticate(form.password.data):
            flash("Invalid password", "danger")
            current_app.logger.warning(f'User using invalid password {user.email}')
            return redirect(url_for("auth_blueprint.login"))
        login_user(user, remember=form.remember_me.data)
        current_app.logger.info(f'Login for {user.email}')
        return redirect(url_for("platform_blueprint.index"))
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
        user.send_activation_email(token)
        flash("Congratulations, you are now a registered user! Check you email for an activation link", "success")
        new_event(EventTypes.NEW_USER, user.email)
        current_app.logger.info(f'New registration {form.email.data}')
        return redirect(url_for("auth_blueprint.login"))
    return render_template("auth/register.html", form=form)


@auth_blueprint.route("/activate/<token>", methods=["GET"])
def activate(token):
    email = token_user_id(token, "REGISTRATION")
    user = User(email)
    user.activate()
    flash("Congratulations! Your account is activated!", "success")
    current_app.logger.info(f'User activated {user.email}')
    return redirect(url_for("auth_blueprint.login"))


@auth_blueprint.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User(form.email.data)
        token = create_token("PASSWORD_RESET", user.email)
        user.send_password_reset_email(token)
        current_app.logger.info(f'Password reset link sent to {user.email}')
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
        current_app.logger.info(f'Password updated for {user.email}')
        return redirect(url_for("auth_blueprint.login"))
    return render_template("auth/password_reset.html", form=form)
