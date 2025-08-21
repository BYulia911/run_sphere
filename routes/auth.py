from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
import bcrypt
import os
from db import db  
from models import User

auth = Blueprint('auth', __name__)

@auth.route('/')
def home():
    return render_template('index.html')

# Регистрация
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        height = request.form.get('height')
        weight = request.form.get('weight')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')

        avatar = request.files.get('avatar')
        avatar_filename = None

        if avatar:
            avatar_data = avatar.read()
        else:
            if gender == 'male':
                default_avatar_path = os.path.join('static', 'uploads', 'male.png')
            elif gender == 'female':
                default_avatar_path = os.path.join('static', 'uploads', 'female.png')
            else:
                default_avatar_path = os.path.join('static', 'uploads', 'default.png')
            with open(default_avatar_path, 'rb') as f:
                avatar_data = f.read()

        if (User.query.filter_by(username=username).first() or
            User.query.filter_by(email=email).first()):
            flash("Пользователь уже существует")
            return render_template('register.html', email=email, username=username)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password,
                        height=height, weight=weight, date_of_birth=date_of_birth, gender=gender,
                        avatar=avatar_data)
        db.session.add(new_user)
        db.session.commit()

        flash("Пользователь зарегистрирован")
        return redirect(url_for('auth.home'))

    return render_template('register.html')

# Авторизация
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Пользователь не найден")
            return redirect(url_for('auth.home'))

        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Успешный вход")
            return redirect(url_for('profile.profile_view'))

        else:
            flash("Неверный пароль")
            return redirect(url_for('home'))

    return render_template('login.html')

# Выход из системы
@auth.route('/logout')
def logout():
    session.clear()
    flash("Вы вышли из системы.")
    return redirect(url_for('auth.home'))