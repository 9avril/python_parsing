import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
from settings import nrdt_server, nrdt_user, nrdt_password

options = Options()
options.add_argument("--window-size=1920,1200")
options.add_argument("--headless")

driver = webdriver.Chrome()
driver.get(nrdt_server)

id_box = driver.find_element(By.ID, 'email')
id_box.send_keys(nrdt_user)

pass_box = driver.find_element(By.ID, 'passwd')
pass_box.send_keys(nrdt_password)

login_button = driver.find_element(By.ID, 'login')
login_button.click()

alert = driver.switch_to.alert.accept()

# очистка файла перед началом записи
with open("hosts_scraping.txt", "w") as file:
    pass


def network_config_view_host(host):
    global configure_btn
    network_config_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Network Config')))
    network_config_button.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'text')))
    driver.find_element(By.ID, 'text').clear()
    hostname_box = driver.find_element(By.ID, 'text')
    hostname_box.send_keys(host)

    filter_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btnFilter")))
    filter_button.click()

    cards_info = []

    try:
        time.sleep(2)
        host_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id,'jqg_ip-address-host-list')]")))
        host_button.click()
        time.sleep(2)

        open_host_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btnOpenIPAddressHost")))
        open_host_button.click()

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, features="html.parser")

        rows = soup.find_all('div', {"class": re.compile("form-field surround")})
        shelf_link = driver.find_element(By.ID, 'hostDesignShelf')
        shelf_link.click()
        time.sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        for row_div in soup.select('#shelf-container > div'):
            row = row_div.find('h2').text.strip()

            for item_container in row_div.select('.itemContainer'):
                if "empty" in item_container.get("class"):
                    un_equipped = item_container.contents[0].strip()
                    cards_info.append({'card_num': None, 'line': f"{un_equipped}\n"})
                else:
                    card_num = item_container.find(class_='itemHeader').strong.text.strip()
                    card_name = item_container.find(class_='item-link').text.strip()
                    card_type = item_container.find_all('strong')[-1].next_sibling.strip()
                    part_number = item_container.find(class_='itemDescription').strong.next_sibling.strip()

                    line = f"{card_num} Card: {card_name}; Type: {card_type}; Part Number: {part_number};"
                    cards_info.append({'card_num': card_num, 'line': f"{line}\n"})
                    configure_btn = driver.find_elements(By.CLASS_NAME, "configureItem")

        for btn in configure_btn:
            btn.click()
            time.sleep(2)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            item_container = soup.find(class_="itemContainer")

            item_header = item_container.find(class_='itemHeader')
            card_num = item_header.strong.text.strip()

            item_link = item_container.find(class_='item-link')
            card_name = item_link.text.strip()

            strong_elements = item_container.find_all('strong')
            card_type = strong_elements[-1].next_sibling.strip()

            item_description = item_container.find(class_='itemDescription')
            part_number = item_description.strong.next_sibling.strip()

            sub_port_item = item_container.find(class_='sub-port-item')
            ports = sub_port_item.strong.text.strip()

            line = f"{card_num} Card: {card_name}; Type: {card_type}; Part Number: {part_number};\nPorts\n{ports}"
            for i in range(len(cards_info)):
                if cards_info[i]['card_num'] == card_num:
                    cards_info[i]['line'] += f"{line}\n\n"
                    break

            driver.back()
            time.sleep(2)

            # Запись всей информации о картах в файл в нужном порядке
            with open("hosts_scraping.txt", "a") as file:
                for card_info in cards_info:
                    file.write(card_info['line'])

    except Exception as e:
        print("Exception? \n", e)


host_list = ["ashs-sbam-01", "MSCS-ACCR-01"]

for hosts in host_list:
    network_config_view_host(hosts)

driver.quit()
