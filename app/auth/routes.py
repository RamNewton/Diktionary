from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from app.auth.forms import *
from app import db
from app.auth import bp
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # print("GET")
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        # print("POST")
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
                    firstname = form.firstname.data,
                    lastname = form.lastname.data,
                    email = form.email.data,
                    username = form.username.data
                )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('New User successfully registered!')
        return redirect(url_for('main.index'))
    else:
        return render_template('auth/register.html', title = 'Register', form = form)
        