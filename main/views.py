from django.shortcuts import render
from urllib.request import *
from bs4 import BeautifulSoup

import http.client
http.client._MAXHEADERS = 1000


def get_home_page(request):
    return render(request, 'main/home_page.html')


def get_cinemas_page(request):
    return render(request, 'main/cinemas_page.html')


def parse_genre_and_time_duration(children):
    """parsing the genre and time of the movie to the list"""
    set_p = children.find_all('p')
    if set_p[0].string is None:
        set_p[0].string = 'Неизвестно'
    return set_p


def get_cinema_city_page(request):
    host = "https://cinemaciti.ua/"
    url = "https://cinemaciti.ua/fontan-sky-center/rozklad"
    html = urlopen(url)
    bsObj = BeautifulSoup(html.read(), 'html.parser')
    full_info = dict()
    count = 0
    for item in bsObj.findAll("div", class_="session clear"):
        result = dict()
        count = count + 1
        # genre & time_duration
        genre_time = parse_genre_and_time_duration(item)
        children = item.findChildren(recursive=True)
        for child in children:
            # name
            if child.name == "a" and 'class' in child.attrs and child.attrs['class'][0] == 'session__movie-name':
                name = child.contents[0]
            # link
            if child.name == "a" and 'class' in child.attrs and child.attrs['class'][0] == 'session__movie-name':
                link = host + child.attrs['href']

        full_info[count] = result
        result['genre_time'] = genre_time
        result['name'] = name
        result['link'] = link

    return render(request, 'main/cinema_city.html', context={'full_info': full_info})
