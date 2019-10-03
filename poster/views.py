from django.shortcuts import redirect, render


def redirect_home_page(request):
    return redirect('home_page_url', permanent=True)


def handler500(request):
    return render(request, 'errors/500.html', status=500)


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)
