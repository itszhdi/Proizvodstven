from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.db import connection
import re
from datetime import datetime
from django.urls import reverse


def get_event_data(event_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    event_name, 
                    event_date, 
                    description, 
                    category, 
                    name AS organizer_name, 
                    time, 
                    address, 
                    photo_path, 
                    price,
                    timer(event_id) AS timer,
                    event_id
                FROM Events
                JOIN Categories USING (category_id)
                JOIN Organizers USING (organizer_id)
                JOIN Tickets USING (event_id)
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
                    'price': row[8],
                    'timer': row[9],
                    'id': row[10]
                }
                if row[9] == '0':
                    event_data['timer'] = 'SOLD OUT!'

                return event_data
            else:
                return None
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None




def enter_card_data(request, event_id):
    if request.method == "POST":
        card_number = request.POST.get('card')
        date = request.POST.get('date', '')
        cvv = request.POST.get('cvv', '')

        card_number_regex = r'^\d{16}$'
        if not re.match(card_number_regex, card_number):
            messages.error(request, "Номер карты должен содержать 16 цифр без пробелов.")
            return False

        try:
            expiry_date = datetime.strptime(date, "%m/%y")
            if expiry_date < datetime.now():
                messages.error(request, "Введите корректную дату.")
                return False
        except ValueError:
            messages.error(request, "Введите корректную дату в формате MM/YY.")
            return False

        cvv_regex = r'^\d{3}$'
        if not re.match(cvv_regex, cvv):
            messages.error(request, "CVV код должен содержать 3 цифры.")
            return False

    return True





def open_event_page(request, event_id):
    event_data = get_event_data(event_id)

    if request.method == "POST":
        if not enter_card_data(request, event_id):
            return redirect(reverse('event', args=[event_id]))
        else:
            return redirect(reverse('buy', args=[event_id]))

    if event_data is None:
        return render(request, 'mainpage/main_page.html')

    return render(request, 'eventpage/event.html', {'event': event_data})




EXTERNAL_SITES = {
    'kaspi': 'https://kaspi.kz/',
    'qiwi': 'https://qiwi.com/',
}

def buy_ticket(request, event_id):
    event_data = get_event_data(event_id)
    return render(request, 'eventpage/buy.html', {'event': event_data})

def redirect_to_site(request, site, event_id):
    event_data = get_event_data(event_id)

    if site not in EXTERNAL_SITES:
        return HttpResponse("Invalid site identifier", status=404)

    external_url = EXTERNAL_SITES[site]
    return render(request, 'eventpage/buy.html', {
        'event': event_data,
        'external_url': external_url})



def search_event(request):
    search = request.POST.get('search')
    if not search:
        return render(request, 'eventpage/search.html', {'error': 'Введите название мероприятия для поиска.'})
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT event_id FROM Events 
                WHERE event_name ILIKE %s;
            """, [f"%{search}%"])
            row = cursor.fetchone()
    except Exception as e:
        print(f"Error! {e}")
        return render(request, 'eventpage/search.html', {'error': 'Ошибка при выполнении поиска.'})

    if row is not None:
        event_id = row[0]
        event_data = get_event_data(event_id)
    else:
        event_data = None
    return render(request, 'eventpage/search.html', {'event': event_data, 'search': search})
