from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from models import User
import bcrypt
import os
from app import db

profile = Blueprint('profile', __name__)

# Профиль
@profile.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Пожалуйста, войдите в систему.")
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

# Редактирование профиля
@profile.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('Пользователь не найден.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        
        new_password = request.form['password']
        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed_password.decode('utf-8')
        
        user.height = int(request.form['height'])
        user.weight = float(request.form['weight'])
        user.age = int(request.form['age'])
        user.gender = request.form['gender']

        if user.gender == 'male':
            user.avatar = 'male.png'
        elif user.gender == 'female':
            user.avatar = 'female.png'
        else:
            user.avatar = 'default.png'
        
        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            if avatar_file and allowed_file(avatar_file.filename):
                filename = secure_filename(avatar_file.filename)
                avatar_file.save(os.path.join('static/avatars', filename))
                user.avatar = f'avatars/{filename}'

        try:
            db.session.commit()
            flash('Данные профиля успешно обновлены.')
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка при обновлении данных: {str(e)}')

        return redirect(url_for('profile', user_id=user.id))

    return render_template('edit_profile.html', user=user)

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

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
        return redirect(url_for('profile'))