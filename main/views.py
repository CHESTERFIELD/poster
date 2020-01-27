import datetime
import re
import http.client
import urllib
import time

from django.http import Http404, HttpResponse
from django.shortcuts import render
from urllib.request import *
from bs4 import BeautifulSoup, NavigableString, Tag
from requests import HTTPError
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
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
    """redirect from host on home_page"""
    return render(request, 'main/home_page.html')


def get_cinemas_page(request):
    return render(request, 'main/cinemas_page.html')


def get_cinema_city_page(request):
    """
    parse cinema item from cinema_city
    """
    host = "https://cinemaciti.ua"
    url = "https://cinemaciti.ua/fontan-sky-center/rozklad"
    html = urlopen(url)
    bsObj = BeautifulSoup(html.read(), 'html.parser')
    full_info = dict()
    count = 0
    for item in bsObj.findAll("div", class_="session clear"):
        result = dict()
        count = count + 1

        # name
        for item_inner in item.find("a", class_="session__movie-name"):
            if type(item_inner) is NavigableString:
                name=str(item_inner)
                result['name'] = str(item_inner)

        # genre
        for item_inner in item.findAll('div', class_="session__about-movie")[0]:

            if type(item_inner) is NavigableString:
                continue

            if item_inner.next.string == "Жанр":
                continue
            else:
                result['genre'] = item_inner.next.string

        # time
        try:
            for item_inner in item.findAll('div', class_="session__about-movie")[1]:

                if type(item_inner) is NavigableString:
                    continue

                if item_inner.next.string == "Час":
                    continue
                else:
                    result['time'] = item_inner.next.string

        except IndexError:
            result['time'] = 'Неизвестно'

        # link
        result['link'] = host + item.find("a").attrs['href']

        # schedule
        schedule = dict()

        for block in item.find_all("div", class_="session__block"):

            tape = block.find('div', class_="session__type").string

            block_info = dict()
            number = 0

            for info_block in block.find_all('a', class_='session-block'):
                info = dict()
                number = number + 1

                for schedule_block in info_block.find("div", class_="session-block__time"):
                    info['block_time'] = schedule_block.string

                for schedule_block in info_block.find("div", class_="session-block__price"):
                    info['block_price'] = schedule_block.string

                block_info[number] = info

            schedule[tape] = block_info

        result["schedule"] = schedule

        full_info[count] = result

    # print(full_info)
    return render(request, 'main/cinema_city.html', context={'full_info': full_info})


def parse_genre_and_time_duration_planeta(link):
    """
    parse genre and time cinema item from planetakino
    """
    # set_dd = list()
    hdr = {'User-Agent': 'Chrome/5.0'}
    req = Request(link, headers=hdr)
    page = urlopen(req)

    soup = BeautifulSoup(page.read(), "html.parser")

    element_genre = soup.find(text="Жанр").find_next("dd").text
    element_time =  soup.find(text="Тривалість").find_next("dd").text

    # print(element_genre)
    # print(element_time)

    return element_genre, element_time


def get_planeta_kino_page(request):
    a = datetime.datetime.now()
    host = "https://planetakino.ua"
    url = "https://planetakino.ua/odessa2/showtimes/#today"
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    html = driver.page_source
    full_info = dict()
    result = dict()
    count = 0
    app_timetable_movie = 0
    soup = BeautifulSoup(html, "html.parser")
    for element in soup.find('app-root'):

        for child_element in element.findAll('div', class_="movie"):
            # print(child_element)
            for child in child_element.findAll('a', class_='tablet-movie-name'):

                if child.name == "a" and 'class' in child.attrs and child.attrs['class'][0] == 'tablet-movie-name':
                    # name
                    name = child.string
                    count = count + 1
                    app_timetable_movie += 1
                    result['name'] = name
                    print(name)
                    # link
                    link = host + child.attrs['href']
                    result['link'] = link
                    genre, time = parse_genre_and_time_duration_planeta(link)
                    # genre
                    result['genre'] = genre
                    # time
                    result['time'] = time

                # schedule
                schedule = dict()
                div = 1
                for schedule_div in child_element.find_all("div", class_="tech t-mb-10-l"):
                    div += 1
                    technology = schedule_div.find('span', class_="technology-title t-mb-7").string
                    # print(schedule_div)
                    block_info = dict()
                    number = 0
                    app_seance_chips = 0

                    for info_block in schedule_div.find_all('button', class_='chips'):
                        info = dict()
                        app_seance_chips += 1
                        # print(info_block)
                        # print(dir(info_block))

                        if info_block.has_attr("disabled"):
                            pass
                        else:
                            number = number + 1
                            time = info_block.string
                            info['block_time'] = time
                            print(time)
                            xpath = "/html/body/div[1]/div/app-root/app-general-timetable/section/section[2]/app-timetable-movie[{0}]/div/section/div/div[{1}]/div/app-seance-chips[{2}]/button".format(app_timetable_movie, div, app_seance_chips)
                            element_to_hover_over = driver.find_element_by_xpath(xpath)
                            hover = ActionChains(driver).move_to_element(element_to_hover_over)
                            hover.perform()

                            htmll = driver.page_source
                            soupp = BeautifulSoup(htmll, "html.parser")

                            price_list = list()

                            try:
                                for chips_box in soupp.find_all('div', class_='cash'):
                                    print(chips_box)
                                    price_list.append(int(str(chips_box.string).split(" ")[0]))
                            except TypeError:
                                pass

                            print(price_list)
                            try:
                                price = "от {0} до {1} грн.".format(min(price_list), max(price_list))
                            except ValueError:
                                price = ""
                            info['block_price'] = price

                        block_info[number] = info

                    schedule[technology] = block_info

                result["schedule"] = schedule

            full_info[count] = result.copy()
    if 0 in full_info:
        del full_info[0]
    print(full_info)
    b = datetime.datetime.now()
    c = b - a
    print(int(c.total_seconds()))
    driver.close()
    return render(request, 'main/cinema_city.html', context={'full_info': full_info})


def get_min(string):
    """
    get minutes in format 'sec хв.' for def parse_genre_and_time_duration_multiplex
    """
    h, m = string.split(":")
    minutes = str(int(h) * 60 + int(m)) + " хв."
    return minutes


def parse_genre_and_time_duration_multiplex(host, link):
    set_genre_time = list()
    html = urlopen(link)
    soup = BeautifulSoup(html.read(), 'html.parser')

    for element in soup.find_all("ul", class_="movie_credentials"):

        for genres in element.find_all("a", href=re.compile("genre")):
            set_genre_time.append(genres.text)

        for times in element.find_all("p", class_="val", text=re.compile(":")):
            if type(times) is NavigableString:
                continue
            else:
                time = get_min(times.text.strip())

    return set_genre_time, time


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
        result['name'] = element.attrs['title']
        link = host + element.attrs['href']
        result['link'] = link
        result['genre'], result['time'] = parse_genre_and_time_duration_multiplex(host, link)

        for film in element.findParents("div", class_="film"):
            block_info = dict()
            number = 0

            for schedule_item in film.find_all("div", class_="ns"):
                info = dict()
                number = number + 1

                info["time"] = schedule_item.find("p", class_='time').text

                info["tag"] = schedule_item.find("p", class_="tag").text

                schedule_item_min_cost = int(schedule_item.attrs['data-low']) / 100
                schedule_item_max_cost = int(schedule_item.attrs['data-high']) / 100
                info['price'] = "от " + str(int(schedule_item_min_cost)) + " до " + str(int(schedule_item_max_cost)) + " грн."

                block_info[number] = info

            result['schedule'] = block_info

        full_info[count] = result

    # print(full_info)
    return render(request, 'main/multiplex.html', context={'full_info': full_info})


def get_concerts_from_tickets_od_ua(request):
    data = "концертов"
    type = "type-icon type1"
    template = "main/concerts.html"
    return HttpResponse(get_data_from_tickets_od_ua(request, template, type, data))


def get_theatre_from_tickets_od_ua(request):
    data = "спектаклей"
    type = "type-icon type2"
    template = "main/theatre.html"
    return HttpResponse(get_data_from_tickets_od_ua(request, template, type, data))


def get_children_from_tickets_od_ua(request):
    data = "сеансов"
    type = "type-icon type4"
    template = "main/children.html"
    return HttpResponse(get_data_from_tickets_od_ua(request, template, type, data))


def get_show_from_tickets_od_ua(request):
    data = "сеансов"
    type = "type-icon type3"
    template = "main/show.html"
    return HttpResponse(get_data_from_tickets_od_ua(request, template, type, data))


def get_data_from_tickets_od_ua(request, template, type, data):
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

        #name
        for item_inner in parent.find('span', class_='summary'):
            result['name'] = item_inner.string

        #current_place
        for item_inner in parent.find('span', class_='place fn org location'):
            result['current_place'] = item_inner.string

        #cost
        for item_inner in parent.find(text=re.compile(cost_string)):
            cost = item_inner.split()
            if not cost:
                continue
            else:
                full_cost = full_cost + "".join(cost)
        result['cost'] = " ".join(re.split('(\d+)', full_cost))

        #link
        result['link'] = host + parent.find("a").attrs["href"]

        #time
        for item_inner in parent.find_all('span', class_='search-item-attr'):
            result['time'] = item_inner.find('a').string

        full_info[count] = result

    if bool(full_info):
        return render(request, template, context={'full_info': full_info})
    else:
        return render(request, 'main/empty_page.html', context={'place': data})
