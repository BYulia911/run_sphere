from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
import bcrypt
import os

# Импортируйте db из db.py
from db import db  
from models import User  # Импортируйте User после db

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
        age = request.form.get('age')
        gender = request.form.get('gender')

        avatar = request.files.get('avatar')
        avatar_filename = None

        if avatar:
            avatar_filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(current_app.config['UPLOAD_FOLDER'], avatar_filename))
        else:
            if gender == 'male':
                avatar_filename = 'male.png'
            elif gender == 'female':
                avatar_filename = 'female.png'
            else:
                avatar_filename = 'default.png'

        if (User.query.filter_by(username=username).first() or
            User.query.filter_by(email=email).first()):
            flash("Пользователь уже существует")
            return render_template('register.html', email=email, username=username)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, email=email, password=hashed_password,
                        height=height, weight=weight, age=age, gender=gender,
                        avatar=avatar_filename)
        db.session.add(new_user)
        db.session.commit()

        flash("Пользователь зарегистрирован")
        return redirect(url_for('home'))

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

        if bcrypt.checkpw(password.encode('utf-8'), user.password):
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