from django.shortcuts import render, redirect
from django.http import Http404
from eventpage.views import get_event_data
def show_main_page(request):
    return render(request, 'mainpage/main_page.html')

def event_detail(event_id):
    event_data = get_event_data(event_id)
    print(get_event_data())
    if event_data:
        return redirect('event')
    else:
        raise Http404("Страница не найдена")
