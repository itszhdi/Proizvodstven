from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection
from django.contrib import messages
from regandaut.views import check_user_password
import base64


# Функция проверки текущего пароля (проверка для изменения данных)
def check_current_password(request,password):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Пользователь не авторизован.")
        return False
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

    if not check_password(password, stored_password):
        return False
    return True

# Функция выбора информации из базы данных
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

# Функция для корректной работы страницы профиля
def render_info(request):
    user_id = request.session.get('user_id')
    if not user_id:  # Если пользователь не авторизован
        messages.error(request, "Пользователь не авторизован.")
        return redirect('authorize')

    if request.method == 'GET':
        user_data = get_user_info(user_id) or {}  # Получаем информацию о пользователе
        organizer = user_status(user_id)  # Проверяем, является ли пользователь организатором
        return render(request, 'userpage/profile.html', {'user': user_data, 'organizer': organizer})

    elif request.method == 'POST':
        if 'change_password' in request.POST:
            return update_password(request)
        elif 'change_mail' in request.POST:
            return update_mail(request)
        elif 'change_name' in request.POST:
            return update_name(request)
        elif 'delete_account' in request.POST:
            return delete_user_info(request)

        else:
            messages.error(request, "Неизвестный запрос!")
            return redirect('profile')


# Функция для удаления аккаунта пользователем
def delete_user_info(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Пользователь не авторизован.")
        return False
    if request.method == 'POST':
        password = request.POST.get('password')

        if not check_current_password(request, password):
            messages.error(request, "Неверный текущий пароль!")
            return redirect('user')
        else:
            with connection.cursor() as cursor:
                cursor.execute("""
                DELETE FROM Customers
                WHERE user_id = %s;
                """, [user_id])
            return redirect('main_page')


# Функция для смены имени пользователем
def update_name(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Пользователь не авторизован.")
        return False

    if request.method == 'POST':
        new_name = request.POST.get('user_name')
        if not new_name:
            messages.error(request, "Имя пользователя не может быть пустым.")
            return redirect('user')

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Customers
                    SET user_name = %s
                    WHERE user_id = %s
                """, [new_name, user_id])

            messages.success(request, "Имя успешно обновлено.")
            return redirect('user')

        except Exception as e:
            print(f"Error updating name: {e}")
            messages.error(request, "Произошла ошибка!")
            return redirect('user')


# Функция для смены пароля пользователем
def update_password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Пользователь не авторизован.")
        return False

    if request.method == 'POST':
        old_password = request.POST.get('old-password')
        new_password = request.POST.get('new-password')
        new_password_confirm = request.POST.get('new-password-confirm')

        if not check_user_password(new_password):
            messages.error(request, "Пароль должен содержать не менее 8 символов, включая буквы и цифры.")
            return redirect('user')

        if not check_current_password(request,old_password):
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


# Функция для смены почты пользователем
def update_mail(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Пользователь не авторизован.")
        return False

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


# Функция определения статуса - организатор или пользователь
def user_status(user_id):
    if not user_id:
        return False
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM Organizers
                    WHERE user_id = %s);""", [user_id])
            result = cursor.fetchone()
            return result[0] if result else False
    except Exception as e:
        print(f"Ошибка базы данных: {e}")
        return False



def logout_user(request):
    # Завершает текущую сессию
    request.session.flush()
    return redirect('authorize')



def open_adder_page(request):
    return render(request, 'userpage/add_event.html')


def add_event(request):
    if request.method == 'POST':
        # Получение данных из формы
        event_name = request.POST.get('event_name')
        description = request.POST.get('description')
        organizer = request.POST.get('organizer')
        category = request.POST.get('category')
        city = request.POST.get('city')
        address = request.POST.get('address')
        event_date = request.POST.get('event_date')
        time = request.POST.get('time')
        photo_path = request.FILES.get('photo_path')
        poster_base64 = request.POST.get('poster_base64')  # Получаем Base64-строку

        # Декодирование Base64 в бинарный формат
        poster_binary = base64.b64decode(poster_base64.split(",")[1])

        # Сохранение данных в базу
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                            INSERT INTO Events (event_name, description, organizer_id, category_id, city, address, event_date, time, poster_data)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, [event_name, description, organizer_id, category_id, city, address, event_date, time,
                              poster_binary])
            messages.success(request, "Событие успешно добавлено!")
        except Exception as e:
            print(f"Ошибка: {e}")
            messages.error(request, "Не удалось сохранить событие.")
        return redirect('events_list')

