from geopy.geocoders import Nominatim
import json
import requests
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright

def split_text(text):
    # Split text
    lines = text.split('Teléfono:')
    address = lines[0].replace("Dirección:","").replace("\n","")
    lines = lines[1].split("Horario de atención:")
    phone = lines[0].replace("Teléfono:","").replace("\n"," ")
    time = lines[1].replace("Horario de atención:","").replace("\n","",1).split("\n")
    return  [address,phone,time]


def get_coordinates_by_address(address):
    geolocator = Nominatim(user_agent="my_geocoder", timeout=20)
    location = geolocator.geocode(address)

    if location:
        return [location.latitude, location.longitude]
    else:
        return None


def get_page_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=0)
        page.wait_for_load_state('load',timeout=0)
        page_content = page.content()
        browser.close()
    return page_content

def get_all_urls(url):
    page = get_page_content(url)
    soup = bs(page,"html.parser")
    all_links = soup.find("li", class_="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children menu-item-512")
    all_links = all_links.find_all("a",class_="elementor-sub-item")
    urls=[]
    for link in all_links:
        urls.append(link.get("href"))
    return urls


#______________Start__________________
URLS = get_all_urls("https://www.santaelena.com.co/")
json_data = []
for URL in URLS:
    page = get_page_content(URL)
    soup = bs(page,"html.parser")
    city = soup.find("h2",class_="elementor-heading-title elementor-size-default").text.split()[-1]
    print(city)
    names = soup.find_all("h3", class_="elementor-heading-title elementor-size-default")
    addresses = soup.find_all("div", class_="elementor-text-editor elementor-clearfix")
    info_shops = []
    for el in addresses:
        if "Horario de atención" in el.text:
            info_shops.append(split_text(el.text))
    print(info_shops)
    print(len(info_shops))
    for i in range(len(names)):
        if "Sur" in info_shops[i][0]:
            address = info_shops[i][0].split("Sur", 1)
        else: address = info_shops[i][0].split("Local", 1)
        json_data.append({
            "name": "Pastelería Santa Elena " + names[i].text,
            "address": city+", " + info_shops[i][0],
            "latlon": get_coordinates_by_address(city+", "+address[0]),
            "phones": info_shops[i][1],
            "working_hours": info_shops[i][2]
        })

with open('script3.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(json_data,ensure_ascii=False, indent=4))



