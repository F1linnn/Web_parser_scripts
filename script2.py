import json
import requests
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright


def get_work_time(url):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        # Find all elements <span> with class "link link--black"
        span_elements = page.query_selector_all('span.link.link--black')

        dict = {}
        for span in span_elements:
            span.click()
            soup = bs(page.content(), "html.parser")
            adres = soup.find("div", class_="address")
            time = soup.find_all("div", class_="work-time")
            t = []
            for el in time:
                t.append(el.text.replace('\n', ' '))
            dict[adres.text] = t
        browser.close()
        return dict

def get_page_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=0)
        page.wait_for_load_state('load',timeout=0)
        page_content = page.content()
        browser.close()
    return page_content

def find_all_urls():
    URL = "https://omsk.yapdomik.ru"
    page = requests.get(URL)

    soup = bs(page.text,"html.parser")
    all_urls_html_code = soup.find_all("a", class_="city-select__item")

    URLS = []
    for url in all_urls_html_code:
        site = url.get("href")
        if site:
            URLS.append(site)
        else: print("Ссылки нету")
    URLS = list(set(URLS))
    URLS.insert(0,URL)
    return URLS



#______________Start__________________
URLS = find_all_urls()
result = []
for URL in URLS:
    page = get_page_content(URL+"/about")
    soup = bs(page,"html.parser")

    #______________Start_search_name___________
    a_tag = soup.find('a', class_='site-logo')
    img_tag = a_tag.find('img')
    name = img_tag.get('alt')
    #______________End_search_name___________

    city = soup.find("a", class_="city-select__current link link--underline")
    phone = soup.find("a", class_="link link--black link--underline")

    points_on_map = soup.find_all("li", attrs={'data-latitude':True, 'data-longitude':True})
    addresses = soup.find_all("span", class_="link link--black")

    #___Search__all__addresses__work__time___
    time_dict = get_work_time(URL+"/about")

    #___Assembly__json__file___
    for i in range(len(points_on_map)):
        lat = points_on_map[i]['data-latitude']
        lon = points_on_map[i]['data-longitude']
        address = addresses[i].text.strip()
        time = time_dict[address]
        result.append({
            "name": name,
            "address": city.text+", "+address,
            "latlon": [float(lat), float(lon)],
            "phones": phone.text,
            "time": time
        })

with open('script2.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(result,ensure_ascii=False, indent=4))
