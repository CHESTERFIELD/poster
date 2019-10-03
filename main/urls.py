from django.urls import path, include

from .views import *

urlpatterns = [
    path('', get_home_page, name='home_page_url'),
    path('cinemas/', get_cinemas_page, name='cinemas_page_url'),
    path('cinemas/cinema_city/', get_cinema_city_page, name='cinema_city_url'),
    path('cinemas/planeta_kino/', get_planeta_kino_page, name='planeta_kino_url'),
    path('cinemas/multiplex/', get_multiplex_page, name='multiplex_url'),
    path('concerts/', get_concerts_from_tickets_od_ua, name='concerts_page_url'),
    path('theatre/', get_theatre_from_tickets_od_ua, name='theatre_page_url'),
    path('children/', get_children_from_tickets_od_ua, name='children_page_url'),
    path('show/', get_show_from_tickets_od_ua, name='show_page_url'),
]
