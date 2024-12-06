from django.db import router
from django.shortcuts import render, redirect
from django.http import Http404
from eventpage.views import get_event_data
from django.http import JsonResponse



def show_main_page(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        if city:
            request.session['selected_city'] = city
            return JsonResponse({'status': 'success', 'city': city})
        return JsonResponse({'status': 'error', 'message': 'City not provided'})

    return render(request, 'mainpage/main_page.html')

def event_detail(event_id):
    event_data = get_event_data(event_id)
    if event_data:
        return redirect('event')
    else:
        raise Http404("Страница не найдена")

def show_meme(request):
    return render(request, 'mainpage/meme.html')

