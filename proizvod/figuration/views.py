from django.shortcuts import render
from django.db import connection
from geopy.geocoders import Nominatim

def get_coordinates(address):
    geolocator = Nominatim(user_agent="map_app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None

def get_events_by_city(city=None):
    with connection.cursor() as cursor:
        if city == 'Астана':
            cursor.execute('''
                SELECT event_name, event_id FROM Events
                WHERE city = 'Astana'
                ORDER BY event_date;
            ''')
        elif city == 'Алматы':
            cursor.execute('''
                SELECT event_name, event_id FROM Events
                WHERE city = 'Almaty'
                ORDER BY event_date;
            ''')
        else:
            cursor.execute('''
                SELECT event_name, event_id FROM Events
                ORDER BY event_date;
            ''')
        return cursor.fetchall()


def figure_map(request):
    city = request.session.get('selected_city')
    events = get_events_by_city(city)

    if city == 'Астана':
        template = 'figuration/map_page_astana.html'
    elif city == 'Алматы':
        template = 'figuration/map_page_almaty.html'
    else:
        template = 'figuration/map_page.html'

    return render(request, template, {'city': city, 'events': events})


def figure_astana_map(request):
    events = get_events_by_city('Астана')
    return render(request, 'figuration/map_page_astana.html', {'city': 'Астана', 'events': events})

def figure_almaty_map(request):
    events = get_events_by_city('Алматы')
    return render(request, 'figuration/map_page_almaty.html', {'city': 'Алматы', 'events': events})
