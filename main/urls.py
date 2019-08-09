from django.urls import path, include

from .views import *

urlpatterns = [
    path('', get_home_page, name='home_page_url'),
]
