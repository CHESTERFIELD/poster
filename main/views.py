import re
import http.client

from django.shortcuts import render
from urllib.request import *
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from DateTime import *

http.client._MAXHEADERS = 1000


def full_day():
    dt = DateTime()
    if dt.day() < 10:
        today = "0" + str(dt.day()) + "0" + str(dt.month()) + str(dt.year())
    else:
        today = str(dt.day()) + "0" + str(dt.month()) + str(dt.year())
    print(today)
    return today


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
    full_info = dict()
    count = 0
    soup = BeautifulSoup(html, "html.parser")
    for element in soup.find('app-root'):
        result = dict()
        children = element.findChildren(recursive=True)
        for child in children:
            # name
            if child.name == "a" and 'class' in child.attrs and child.attrs['class'][0] == 'tablet-movie-name':
                name = child.string
                count = count + 1
            # link
            if child.name == "a" and 'class' in child.attrs and child.attrs['class'][0] == 'tablet-movie-name':
                link = host + child.attrs['href']
                genre_time = parse_genre_and_time_duration_planeta(host, link)

        full_info[count] = result
        result['genre_time'] = genre_time
        result['name'] = name
        result['link'] = link
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
