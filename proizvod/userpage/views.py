from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection
from django.contrib import messages
import re

def get_user_info(user_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, user_mail, user_password, user_name FROM Customers WHERE user_id = %s;", [user_id])
            row = cursor.fetchone()
            if row:
                user_data = {
                    'user_id': row[0],
                    'email': row[1],
                    'password': row[2],
                    'name': row[3]
                }
            return user_data
    except Exception as e:
        print(f'Error! {e}')
        return None



def render_info(request):
    user_id = request.session.get('user_id')
    if request.method == 'GET':
        user_data = get_user_info(user_id)
        return render(request, 'userpage/profile.html', {'user': user_data})
    elif request.method == 'POST':
        if 'change_password' in request.POST:
            return update_password(request)
        elif 'change_mail' in request.POST:
            return update_mail(request)



def update_password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Пользователь не авторизован.")
        return redirect('authorize')

    if request.method == 'POST':
        old_password = request.POST.get('old-password')
        new_password = request.POST.get('new-password')
        new_password_confirm = request.POST.get('new-password-confirm')

        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
        if not re.match(password_regex, new_password):
            messages.error(request, "Пароль должен содержать не менее 8 символов, включая буквы и цифры.")
            return redirect('user')

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT user_password FROM Customers WHERE user_id = %s;
                """, [user_id])
                row = cursor.fetchone()

                if row:
                    stored_password = row[0]
                else:
                    messages.error(request, "Пользователь не найден.")
                    return redirect('user')
        except Exception as e:
            print(f"Error fetching password: {e}")
            messages.error(request, "Ошибка при получении данных пользователя.")
            return redirect('user')

        if not check_password(old_password, stored_password):
            messages.error(request, "Неверный текущий пароль!")
            return redirect('user')

        if new_password != new_password_confirm:
            messages.error(request, "Пароли не совпадают!")
            return redirect('user')
        new_hashed_password = make_password(new_password)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Customers
                    SET user_password = %s
                    WHERE user_id = %s
                """, [new_hashed_password, user_id])

            messages.success(request, "Пароль успешно обновлен.")
            return redirect('user')

        except Exception as e:
            print(f"Error updating password: {e}")
            messages.error(request, "Произошла ошибка при обновлении пароля!")



def update_mail(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Пользователь не авторизован.")
        return redirect('authorize')

    if request.method == 'POST':
        new_mail = request.POST.get('new-mail')
        password = request.POST.get('password')

        email_regex = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        if not re.match(email_regex, new_mail):
            messages.error(request, "Введите корректный адрес электронной почты.")
            return redirect('user')

        try:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT user_password FROM Customers WHERE user_id = %s;""", [user_id])
                row = cursor.fetchone()

                if row:
                    stored_password = row[0]
                else:
                    messages.error(request, "Пользователь не найден.")
                    return redirect('user')
        except Exception as e:
            print(f"Error fetching password: {e}")
            messages.error(request, "Ошибка при получении данных пользователя.")
            return redirect('user')

        if not check_password(password, stored_password):
            messages.error(request, "Неверный пароль!")
            return redirect('user')

        try:
            with connection.cursor() as cursor:
                cursor.execute("""UPDATE Customers SET user_mail = %s WHERE user_id = %s""", [new_mail, user_id])

            messages.success(request, "Email успешно обновлен.")
            return redirect('user')

        except Exception as e:
            print(f"Error updating email: {e}")
            messages.error(request, "Произошла ошибка при обновлении email!")
            return redirect('user')



def logout_user(request):
    # Завершает текущую сессию
    request.session.flush()
    return redirect('authorize')