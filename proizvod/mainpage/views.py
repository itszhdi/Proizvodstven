from django.shortcuts import render, redirect
from django.http import Http404
from eventpage.views import get_event_data
from django.http import JsonResponse
from django.db import connection

def get_city(request):
    # Получаем город из cookies, если он не установлен в сессии
    city = request.session.get('selected_city') or request.COOKIES.get('selected_city')
    if city:
        request.session['selected_city'] = city  # Обновляем сессию
    return city

def get_banners():
    with connection.cursor() as cursor:
        cursor.execute("SELECT poster FROM Events WHERE poster IS NOT NULL")
        posters = cursor.fetchall()
    return posters

def show_main_page(request):
    city = get_city(request)
    with connection.cursor() as cursor:
        cursor.execute('''
        SELECT event_id, photo_path FROM Events
        ORDER BY event_date DESC
        LIMIT 8;
        ''')
        event_list = cursor.fetchall()
        posters = get_banners()
    return render(request, 'mainpage/main_page.html', {'city': city, 'events' :event_list, 'posters': posters})


def event_detail(event_id):
    event_data = get_event_data(event_id)
    if event_data:
        return redirect('event')
    else:
        raise Http404("Страница не найдена")


def show_meme(request):
    return render(request, 'mainpage/meme.html')


def set_city(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        city = data.get('city')
        if city:
            request.session['selected_city'] = city
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


