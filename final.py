import time
import re
import codecs
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
import saveToExcel
import os

# Set parameters to start Chrome in headless mode
options = Options()
options.add_argument("--window-size=1920,1200")
options.add_argument("--headless")

# Using Chrome to access web
driver = webdriver.Chrome()
driver.get(nrdt_server)

# Select the id box
id_box = driver.find_element(By.ID, 'email')

# send username
id_box.send_keys(nrdt_user)

# Select the pass box
pass_box = driver.find_element(By.ID, 'passwd')

# send password
pass_box.send_keys(nrdt_password)

# Find login button
login_button = driver.find_element(By.ID, 'login')

# Click login
login_button.click()

# close the alert pop-up after login
alert = driver.switch_to.alert.accept()


def xmcShelfSpec(host):
    # open file
    file = open('hosts_scraping.txt', 'a')

    # select Network Config tab
    network_config_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Network Config')))

    # click network config
    network_config_button.click()

    # Select the Host name box
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'text')))
    driver.find_element(By.ID, 'text').clear()
    hostname_box = driver.find_element(By.ID, 'text')
    hostname_box.send_keys(host)

    # click filter button
    filter_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btnFilter")))
    filter_button.click()

    try:
        host_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id,'jqg_ip-address-host-list')]")))
        host_button.click()

        open_host_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btnOpenIPAddressHost")))
        open_host_button.click()

        link = driver.find_element(By.ID, 'hostDesignShelf')
        link.click()

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, features="html.parser")

        # click to configure
        cards = driver.find_elements(By.CLASS_NAME, 'configureItem')
        ids = [card.get_attribute("data-itemid") for card in cards]
        list1 = []
        file.write("\n" + host + "\n")

        while len(ids) > 0:
            itemid = ids.pop(0)
            xpath = "//input[@data-itemid='" + itemid + "']"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.find_element(By.XPATH, xpath).click()
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, features="html.parser")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "designerDiv")))
            card = driver.find_element(By.XPATH, '//*[@id="designerDiv"]/h2[1]/a')
            file.write("\t" + card.text + ':\n')
            ports = soup.find_all("div", {"class": "port-item"})
            for port in ports:
                if port is not None:
                    try:
                        strong1 = port.find('strong').getText(strip=True)
                        portRelationships1 = port.find("div", {"class": "port-relationship"}).getText(strip=True)
                        print("\n" + strong1 + "\t" + portRelationships1 + "\n\n")
                        file.write("\n" + strong1 + "\t" + portRelationships1 + "\n\n")
                    except Exception as e:
                        print(e)
                else:
                    print("Port is empty")

            items = soup.find_all("div", {"class": "item"})
            for item in items:
                for header in item.find_all('div'):
                    if header is not None:
                        try:
                            strong = header.find('strong').getText(strip=True)
                            type = header.find('a').getText(strip=True)
                            span = header.find('span').getText(strip=True)
                            list1.append("\n" + strong + "\t" + type + "\t" + span + "\n\n")
                        except Exception as e:
                            print(e)
                    else:
                        print("Header is empty")

            subports = soup.find_all("div", {"class": "sub-port-item"})
            for subport in subports:
                if subport is not None:
                    try:
                        subPortStrong = subport.find('strong').getText(strip=True)
                        portRelationships = subport.find("div", {"class": "port-relationship"}).getText(strip=True)
                        element1 = list1.pop(0)
                        file.write(element1)
                        file.write("Ports: " + subPortStrong + "\n" + portRelationships + "\n\n")
                    except Exception as e:
                        print(e)
                else:
                    print("Subport is empty")

            driver.back()

    except (NoSuchElementException, TimeoutException):
        file.write("\n" + host + "  not found \n")
        file.write("\n-----------------------------------\n")
        file.close()

    except Exception as e:
        print("Exception? \n", e)

    file.close()


host_list = ['ashs-sbam-01", "MSCS-ACCR-01']

for host in host_list:
    xmcShelfSpec(host)

saveToExcel.saveToExcel('hosts_scraping.txt')

driver.quit()
