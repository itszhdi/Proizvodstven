from django.contrib import messages
from django.shortcuts import redirect, render
from django.db import connection
from django.http import Http404
from django.contrib.auth.hashers import make_password, check_password
import re

def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        email_regex = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        if not re.match(email_regex, email):
            messages.error(request, "Введите корректный адрес электронной почты.")
            return redirect('register')

        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
        if not re.match(password_regex, password):
            messages.error(request, "Пароль должен содержать не менее 8 символов, включая буквы и цифры.")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Пароли не совпадают!")
            return redirect('register')

        hashed_password = make_password(password)

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Customers WHERE user_mail = %s;", [email])
            if cursor.fetchone()[0] > 0:
                messages.error(request, "Такой пользователь уже существует!")
                return redirect('authorize')

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Customers (user_mail, user_password) VALUES (%s, %s);",
                [email, hashed_password]
            )
        response = redirect('authorize')
        response['Cache-Control'] = 'no-store'
        return response

    return render(request, 'regandaut/registration.html')

def authorize(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_id, user_password FROM Customers WHERE user_mail = %s;", [email])
                user_data = cursor.fetchone()
                if user_data:
                    user_id, stored_password = user_data

                    if check_password(password, stored_password):
                        # Сохраняем данные пользователя в сессии
                        request.session['user_id'] = user_id
                        request.session['email'] = email
                        return redirect('main_page')

                    else:
                        messages.error(request, "Неверно введенные данные!")

                else:
                    messages.error(request, "Вы не зарегистрированы!")

            return redirect('authorize')
        except Exception as e:
            print(f"Error! {e}")
            raise Http404("Страница не найдена")

    return render(request, 'regandaut/authorization.html')
