from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import bcrypt
from flask_mail import Mail, Message
import os
import secrets
from werkzeug.utils import secure_filename

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY') 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/run_sphere'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    avatar = db.Column(db.String(120), default='default.png')
    # reset_token = db.Column(db.String(256), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
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
            avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename))
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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Пользователь не найден")
            return redirect(url_for('home'))

        if bcrypt.checkpw(password.encode('utf-8'), user.password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Успешный вход")
            return redirect(url_for('profile'))

        else:
            flash("Неверный пароль")
            return redirect(url_for('home'))

    return render_template('login.html')

# Удаление профиля
@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Пожалуйста, войдите в систему.")
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        session.clear()
        flash("Профиль успешно удален.")
        return redirect(url_for('home'))
    else:
        flash("Пользователь не найден.")
        return redirect(url_for('profile'))

# Выход из системы
@app.route('/logout')
def logout():
    session.clear()  # Завершение сессии
    flash("Вы вышли из системы.")
    return redirect(url_for('home'))


'''
# Сброс пароля
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bakharevayulia34@gmail.com'  # ваш email
app.config['MAIL_PASSWORD'] = 'Yulia 12'  # ваш пароль
mail = Mail(app)

# Сброс пароля
@app.route('/reset', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = secrets.token_urlsafe(16)
            user.reset_token = token
            db.session.commit()
            
            msg = Message('Сброс пароля', sender='your_email@gmail.com', recipients=[email])
            msg.body = f'Перейдите по следующей ссылке, чтобы сбросить пароль: http://localhost:5000/reset/{token}'
            mail.send(msg)
            flash("Проверьте свою почту для сброса пароля.")
            return redirect(url_for('home'))
        else:
            flash("Пользователь с таким email не найден.")
            return redirect(url_for('reset_password'))

    return render_template('reset_password.html')

# Обработка сброса пароля
@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    user = User.query.filter_by(reset_token=token).first()
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if user:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed_password
            user.reset_token = None
            db.session.commit()
            flash("Пароль успешно обновлен.")
            return redirect(url_for('login'))
        else:
            flash("Неверный токен.")
            return redirect(url_for('home'))

    return render_template('new_password.html')
'''
# Профиль
@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Пожалуйста, войдите в систему.")
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    return render_template('profile.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)