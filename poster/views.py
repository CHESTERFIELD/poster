from django.shortcuts import redirect


def redirect_home_page(request):
    return redirect('home_page_url', permanent=True)
