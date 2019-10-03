import re
import http.client
import urllib

from django.http import Http404, HttpResponse
from django.shortcuts import render
from urllib.request import *
from bs4 import BeautifulSoup
from requests import HTTPError
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from DateTime import *

http.client._MAXHEADERS = 1000


def full_day():
    """ return date in format ddmmyyyy for find DOM element"""
    dt = DateTime()
    if dt.day() < 10 and dt.month() < 10:
        today = "0" + str(dt.day()) + "0" + str(dt.month()) + str(dt.year())
    elif dt.day() < 10 and dt.month() >= 10:
        today = "0" + str(dt.day()) + str(dt.month()) + str(dt.year())
    elif dt.day() >= 10 and dt.month() >= 10:
        today = str(dt.day()) + str(dt.month()) + str(dt.year())
    else:
        today = str(dt.day()) + "0" + str(dt.month()) + str(dt.year())
    return today


def today_url():
    """ return date for url on ticketsOdUa in format yyyy-mm-dd """
    dt = DateTime()
    today = dt.ISO().split()
    return today[0]


def get_home_page(request):
    return render(request, 'main/home_page.html')


def get_cinemas_page(request):
    return render(request, 'main/cinemas_page.html')


def parse_genre_and_time_duration(children):
    """parsing the genre and time of the movie to the list"""
    set_p = children.find_all('p')
    if set_p[0].string is None:
        set_p[0].string = 'Неизвестно'
    print(type(set_p))
    return set_p


def get_cinema_city_page(request):
    host = "https://cinemaciti.ua"
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


def parse_genre_and_time_duration_planeta(host, link):
    set_dd = list()
    hdr = {'User-Agent': 'Chrome/5.0'}
    req = Request(link, headers=hdr)
    page = urlopen(req)


    # mbytes = page.read()
    # htmlstr = mbytes.decode('utf8')
    # htmlstr.replace('<dt name="duration">Тривалість</dt>','</dd>')


    soup = BeautifulSoup(page.read(), "html.parser")
    for element in soup.find_all('span'):
        element.extract()
    for genre in soup.find_all("dd")[3]:
        set_dd.append(genre)
    for time in soup.find_all("dd")[9]:
        set_dd.append(time)
    print(set_dd)
    return set_dd


    # driver = webdriver.Chrome(ChromeDriverManager().install())
    # driver.get(link)
    # html = driver.page_source
    # soup = BeautifulSoup(html, "html.parser")
    # for element in soup.find('div', class_="movie-page-block__summary"):
    #     children = element.findChildren(recursive=True)
    #     print(children)


def get_planeta_kino_page(request):
    host = "https://planetakino.ua"
    url = "https://planetakino.ua/odessa2/showtimes/#today"
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    html = driver.page_source
    driver.close()
    full_info = dict()
    result = dict()
    count = 0
    soup = BeautifulSoup(html, "html.parser")
    for element in soup.find('app-root'):
        children = element.findChildren(recursive=True)
        for child in children:
            # name
            if child.name == "a" and 'class' in child.attrs and child.attrs['class'][0] == 'tablet-movie-name':
                name = child.string
                count = count + 1
                result['name'] = name
            # link
            if child.name == "a" and 'class' in child.attrs and child.attrs['class'][0] == 'tablet-movie-name':
                link = host + child.attrs['href']
                result['link'] = link
                genre_time = parse_genre_and_time_duration_planeta(host, link)
                result['genre_time'] = genre_time
            full_info[count] = result.copy()
    if 0 in full_info:
        del full_info[0]
    print(full_info)
    return render(request, 'main/cinema_city.html', context={'full_info': full_info})


def parse_genre_and_time_duration_multiplex(host, link):
    set_genre_time = list()
    html = urlopen(link)
    soup = BeautifulSoup(html.read(), 'html.parser')
    for element in soup.find_all("a", href=re.compile("genre")):
        set_genre_time.append(element.text)
    return set_genre_time


def get_multiplex_page(request):
    host = "https://multiplex.ua"
    url = "https://multiplex.ua/cinema/odesa/gagarinn_plaza"
    full_info = dict()
    count = 0
    html = urlopen(url)
    soup = BeautifulSoup(html.read(), 'html.parser')
    for element in soup.find_all("a", href=re.compile("#" + full_day()), class_="title"):
        result = dict()
        count = count + 1
        name = element.attrs['title']
        link = host + element.attrs['href']

        full_info[count] = result
        result['genre_time'] = parse_genre_and_time_duration_multiplex(host, link)
        result['name'] = name
        result['link'] = link

    print(full_info)
    return render(request, 'main/multiplex.html', context={'full_info': full_info})


def get_concerts_from_tickets_od_ua(request):
    data = "концертов"
    type = "type-icon type1"
    return HttpResponse(get_data_from_tickets_od_ua(request, type, data))


def get_theatre_from_tickets_od_ua(request):
    data = "спектаклей"
    type = "type-icon type2"
    return HttpResponse(get_data_from_tickets_od_ua(request, type, data))


def get_data_from_tickets_od_ua(request, type, data):
    cost_string = 'грн.'
    host = "https://tickets.od.ua"
    url = "https://tickets.od.ua/?date=" + today_url()
    hdr = {'User-Agent': 'Chrome/5.0'}
    req = Request(url, headers=hdr)

    try:
        page = urlopen(req)
    except urllib.error.HTTPError:
        return render(request, 'main/empty_page.html', context={'place': data})

    soup = BeautifulSoup(page.read(), "html.parser")
    full_info = dict()
    count = 0
    for item in soup.find_all("span", class_=type):
        parent = item.findParent("div", class_="event-item-image")
        print(item)
        result = dict()
        count = count + 1
        full_cost = ""
        for item_inner in parent.find('span', class_='summary'):
            name = item_inner.string
        for item_inner in parent.find('span', class_='place fn org location'):
            current_place = item_inner.string
        for item_inner in parent.find(text=re.compile(cost_string)):
            cost = item_inner.split()
            if not cost:
                continue
            else:
                full_cost = full_cost + "".join(cost)
        true_cost = " ".join(re.split('(\d+)', full_cost))
        link = host + parent.find("a").attrs["href"]
        for item_inner in parent.find_all('span', class_='search-item-attr'):
            time = item_inner.find('a').string

        full_info[count] = result
        result['name'] = name
        result['current_place'] = current_place
        result['cost'] = true_cost
        result['link'] = link
        result['time'] = time

    if bool(full_info):
        return render(request, 'main/theatre.html', context={'full_info': full_info})
    else:
        return render(request, 'main/empty_page.html', context={'place': data})
