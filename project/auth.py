from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import Uzytkownicy
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    if not current_user.is_authenticated:
        return render_template('login.html')
    else:
        return redirect(url_for('main.bet'))


@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = Uzytkownicy.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.haslo, password):
        flash('Błędny login lub hasło.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.bet'))

@auth.route('/signup')
def signup():
    if not current_user.is_authenticated:
        return render_template('signup.html')
    else:
        return redirect(url_for('main.bet'))

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    nazwisko = request.form.get('nazwisko')
    pesel = request.form.get('pesel')
    telefon = request.form.get('telefon')

    user = Uzytkownicy.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Istnieje konto o podanym adresie email')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = Uzytkownicy(
        email=email, 
        haslo=generate_password_hash(password, method='sha256'), 
        pesel=pesel, 
        imie=name, 
        nazwisko=nazwisko, 
        telefon=telefon, 
        uprawnienia='K')

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))