from flask import Blueprint, Response, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
from models import User, WeightTracking
from datetime import datetime
import bcrypt
import base64
import os
import io
from db import db

profile = Blueprint('profile', __name__)

# Профиль
@profile.route('/profile')
def profile_view():
    user_id = session.get('user_id')
    if not user_id:
        flash("Пожалуйста, войдите в систему.")
        return redirect(url_for('auth.login'))
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

# Редактирование профиля
@profile.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('Пользователь не найден.')
        return redirect(url_for('auth.home'))

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        
        new_password = request.form['password']
        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed_password.decode('utf-8')
        
        user.height = int(request.form['height'])
        new_weight = float(request.form['weight'])
        if new_weight != user.weight:
            user.weight = new_weight
            new_weight_entry = WeightTracking(user_id=user.id, weight=new_weight)
            db.session.add(new_weight_entry)
        user.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        user.gender = request.form['gender']

        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            if avatar_file and allowed_file(avatar_file.filename):
                avatar_data = avatar_file.read()
                user.avatar = avatar_data
        try:
            db.session.commit()
            flash('Данные профиля успешно обновлены.')
        except Exception as e:
            db.session.rollback()
            print(f'Error during commit: {str(e)}')
            flash(f'Произошла ошибка при обновлении данных: {str(e)}')
        return redirect(url_for('profile.profile_view'))
    return render_template('edit_profile.html', user=user)

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@profile.route('/avatar/<int:user_id>')
def get_avatar(user_id):
    user = User.query.get(user_id)
    if user and user.avatar:
        return Response(user.avatar, mimetype='image/png')  # Укажите правильный тип изображения
    return '', 404

@profile.route('/weight_trend/<int:user_id>', methods=['GET'])
def weight_trend(user_id):
    weights = WeightTracking.query.filter_by(user_id=user_id).order_by(WeightTracking.recorded_at).all()
    if not weights:
        return "Нет данных о весе для данного пользователя.", 404
    timestamps = [entry.recorded_at for entry in weights]
    weight_values = [entry.weight for entry in weights]

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, weight_values, marker='o')
    plt.title('Изменение веса')
    plt.xlabel('Дата')
    plt.ylabel('Вес (кг)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Сохранение графика в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Кодирование изображения в base64
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f'<img src="data:image/png;base64,{image_base64}"/>'

# Удаление профиля
@profile.route('/delete_profile', methods=['POST'])
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
        return redirect(url_for('profile.delete_profile'))