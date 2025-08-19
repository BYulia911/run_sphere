from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY') 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/run_sphere'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)