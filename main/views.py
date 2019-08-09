from django.shortcuts import render


def get_home_page(request):
    return render(request, 'main/home_page.html')
