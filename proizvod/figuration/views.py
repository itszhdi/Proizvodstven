from django.shortcuts import render

def figure_map(request):
    return render(request, 'figuration/map_page.html')
