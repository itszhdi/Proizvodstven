from django.shortcuts import render

def figure_map(request):
    # Получаем выбранный город из сессии
    city = request.session.get('selected_city')
    if city:
        if city == 'Астана':
            return render(request, 'figuration/map_page_astana.html')
        elif city == 'Алматы':
            return render(request, 'figuration/map_page_almaty.html')
        else:
            return render(request, 'figuration/map_page.html')
    else:
        return render(request, 'figuration/map_page.html')


def figure_astana_map(request):
    return render(request, 'figuration/map_page_astana.html')

def figure_almaty_map(request):
    return render(request, 'figuration/map_page_almaty.html')
