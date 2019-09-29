from django.shortcuts import redirect, render


def redirect_home_page(request):
    return redirect('home_page_url', permanent=True)


def handler500(request):
    return render(request, 'errors/500.html')
