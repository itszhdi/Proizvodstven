from django.shortcuts import redirect, render
from django.db import connection
def open_event_page(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT
        event_name, event_date, description, category, name, time, address, photo_path
        FROM Events
        JOIN Categories USING (category_id)
        JOIN Organizers USING (organizer_id)
        WHERE event_id = %s;""", [2])
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
                'image': row[7]
            }
        else:
            event_data = None

    return render(request, 'eventpage/event.html', {'event': event_data})

def buy_ticket(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT
        event_name, event_date, time, address, price
        FROM Events
        JOIN Tickets USING (event_id)
        WHERE event_id = %s;""", [2])
        row = cursor.fetchone()

        if row:
            info = {
                'event': row[0],
                'date': row[1],
                'time': row[2],
                'place': row[3],
                'price': row[4]
            }
        else:
            info = None
    return render(request, 'eventpage/buyTicket.html', {'event': info})