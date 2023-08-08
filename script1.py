import json
import requests
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright


def get_page_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=0)
        page.wait_for_load_state('load',timeout=0)
        page_content = page.content()
        browser.close()
    return page_content


def get_urls_of_cities():
    URL = "https://dentalia.com/"
    r = requests.get(URL)

    soup = bs(r.text, "html.parser")

    sections = soup.find_all('section',
                             class_='elementor-section elementor-inner-section elementor-element elementor-element-01a0b47 LinkToClinic elementor-section-boxed elementor-section-height-default elementor-section-height-default')
    URLS_of_cityes = []
    if sections:
        # Iterate over found section elements and extract the value of the 'id' attribute
        for section in sections:
            section_id = section.get('id')
            if section_id:
                URLS_of_cityes.append(section_id)
            else:
                print("The section element is missing an 'id' attribute.")
    else:
        print("Empty!")

    return URLS_of_cityes



#______________Start__________________
URLS = get_urls_of_cities()
json_lst = []
for url in URLS:
    page_content = get_page_content(url)
    soup = bs(page_content,"html.parser")

    names_of_clinics = soup.find_all("h3", class_ = "elementor-heading-title elementor-size-default")

    info_clinics = soup.find_all("div", class_ = "jet-listing-dynamic-field__content")

    #Get the id of the clinic to search for coordinates on the map
    info_map_ids = soup.find_all("div", class_ = "jet-listing-grid__items grid-col-desk-1 grid-col-tablet-1 grid-col-mobile-1 jet-listing-grid--330")

    #Get coordinates
    info_on_map = soup.find_all("div", class_ = "jet-map-listing google-provider")

    div_elements = info_map_ids[0].find_all('div',attrs={"data-post-id": True})
    ids_of_coordinates = [div.get("data-post-id") for div in div_elements]
    coordinates_on_map = json.loads(info_on_map[0].get("data-markers"))
    all_coordinates = []


    # Create list of all coordinates
    for id in ids_of_coordinates:
        for item in coordinates_on_map:
            if item['id'] == int(id):
                all_coordinates.append([float(item['latLang']['lat']),float(item['latLang']['lng'])])



    #Create json data
    data = {}
    step = 0
    for i in range(len(names_of_clinics)):
        data['name'] = "dentalia "+names_of_clinics[i].text
        data["latlon"] = all_coordinates[i]
        data["address"] = info_clinics[i + step].text
        phones = info_clinics[i + step + 1].text.replace("Teléfono(s):","").split("\n")
        phones.append("8000033682")
        data["phones"] = phones
        data["working_hours"] = info_clinics[i + step +2].text.replace("Horario: ", "").split("\n")
        step+=2
        json_lst.append(data)
        data = {}

json_data = json.dumps(json_lst,ensure_ascii=False, indent=4)

# Write JSON
with open('script1.json', 'w', encoding='utf-8') as file:
    file.write(json_data)
