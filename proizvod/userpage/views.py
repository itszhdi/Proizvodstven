from django.shortcuts import render

def open_profile(request):
    return render(request, 'userpage/profile.html')