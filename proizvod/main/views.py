from django.shortcuts import render

def open_mainpage(request):
    return render(request,'main/index.html')