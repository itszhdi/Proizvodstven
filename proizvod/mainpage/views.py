from django.shortcuts import render

def show_main_page(request):
    return render(request, 'mainpage/main_page.html')
