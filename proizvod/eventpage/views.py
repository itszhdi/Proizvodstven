from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.db import connection
from django.urls import reverse
from django.http import Http404
from django.http import JsonResponse
import pyqrcode


# проверка авторизации пользователя (для ограничения отображения окон)
def check_auth(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    return JsonResponse({'status': 'Authorized'}, status=200)


# получение всей информации о мероприятии
def get_event_data(event_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM event_info
                WHERE event_id = %s;
            """, [event_id])
            row = cursor.fetchone()
            if row:
                event_data = {
                    'name': row[0],
                    'date': row[1],
                    'description': row[2],
                    'category': row[3],
                    'organizer': row[4],
                    'time': row[5],
                    'place': row[6],
                    'image': row[7],
                    'price': 'Free' if int(row[8]) == 0 else row[8],
                    'timer': row[9],
                    'id': row[10],
                    'current': row[11],
                    'ticket_id': row[12],
                    'people_amount': row[13]
                }
                if row[9] == '0' or row[13] == '0':
                    event_data['timer'] = 'SOLD OUT!'

                return event_data
            else:
                return None
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None


# отображение странички мероприятия и сопутствующих ей
def open_event_page(request, event_id):
    event_data = get_event_data(event_id)
    if request.method == "POST":
            return redirect(reverse('buy', args=[event_id]))

    if event_data is None:
        return redirect('main_page')

    from mainpage.views import get_city
    city = get_city(request)
    return render(request, 'eventpage/event.html',
                  {'event': event_data, 'city': city})

# отображение билета со всеми данными
def buy_ticket(request, ticket_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT ticket_id, address, event_name, event_date, time, category
                    FROM Tickets 
                    INNER JOIN Events ON Tickets.event_id = Events.event_id
                    INNER JOIN Categories ON Events.category_id = Categories.category_id
                    WHERE ticket_id = %s""",
                    [ticket_id]
            )
            ticket = cursor.fetchone()

            if not ticket:
                print("Билет не найден в бд")
                return redirect('mytickets')

            event_data = {
                'ticket_id': ticket[0],
                'place': ticket[1],
                'event_name': ticket[2],
                'event_date': ticket[3],
                'time': ticket[4],
                'category': ticket[5]
            }
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return redirect('mytickets')

    return render(request, 'eventpage/buy.html', {'ticket': event_data})


# функция для создания билета
def get_or_create_ticket(event_id, user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT ticket_id, price FROM Tickets WHERE event_id = %s AND user_id IS NOT NULL",
            [event_id]
        )
        existing_ticket = cursor.fetchone()

        if existing_ticket:
            price = existing_ticket[1]
            cursor.execute(
                "INSERT INTO tickets (event_id, user_id, price) VALUES (%s, %s, %s)",
                [event_id, user_id, price]
            )
            return cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE tickets SET user_id = %s WHERE event_id = %s AND user_id IS NULL",
                [user_id, event_id]
            )
            cursor.execute(
                "SELECT ticket_id FROM tickets WHERE event_id = %s AND user_id = %s",
                [event_id, user_id]
            )
            return cursor.fetchone()[0]


EXTERNAL_SITES = {
    'kaspi': 'https://kaspi.kz/',
    'qiwi': 'https://qiwi.com/',
}
# перенаправление на сайты в случае оплаты через каспи и киви
def redirect_to_site(request, site, event_id):
    event_data = get_event_data(event_id)
    if not event_data:
        return JsonResponse({'error': 'Invalid event ID'}, status=404)

    if site not in EXTERNAL_SITES:
        return JsonResponse({'error': 'Invalid site identifier'}, status=404)

    user_id = request.session.get('user_id')
    try:
        ticket_id = get_or_create_ticket(event_id, user_id)
    except Exception as e:
        print(f"Database error: {e}")
        return JsonResponse({'error': 'Database error'}, status=500)

    external_url = EXTERNAL_SITES[site]
    ticket_url = reverse('buy', args=[ticket_id])
    return JsonResponse({
        'external_url': external_url,
        'ticket_url': ticket_url,
    })


# поиск мероприятий
def search_event(request):
    search = request.POST.get('search')
    if not search:
        return redirect('main_page')
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT event_id FROM Events 
                WHERE event_name ILIKE %s;
            """, [f"%{search}%"])
            row = cursor.fetchone()
    except Exception as e:
        print(f"Error! {e}")
        return redirect('main_page')

    if row is not None:
        event_id = row[0]
        event_data = get_event_data(event_id)
    else:
        raise Http404("Страница не найдена")

    from mainpage.views import get_city
    city = get_city(request)
    return render(request, 'eventpage/search.html', {'event': event_data, 'search': search, 'city': city})


# запись заказа на билет в базу данных
def process_order(request, event_id):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        try:
            ticket_id = get_or_create_ticket(event_id, user_id)
            return redirect('buy', ticket_id=ticket_id)
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
            return redirect('event', event_id=event_id)



# === Много функций для генерирования QR кода на билетах ===

# Генерация
def generate_qr_code_from_sql(query_result, file_path):
    qr = pyqrcode.create(query_result)
    qr.png(file_path, scale=6)
    return file_path


def get_query_result(request):
    user_id = request.session.get('user_id')
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT user_id, user_mail, event_name, ticket_id, price 
            FROM Tickets 
            JOIN Customers USING (user_id)
            JOIN Events USING (event_id)
            WHERE user_id = %s""",
            [user_id]
        )
        query_result = cursor.fetchone()[0]

        qr_file_path = "/static/eventpage/img/generated_qr.png"
        generate_qr_code_from_sql(query_result, qr_file_path)


