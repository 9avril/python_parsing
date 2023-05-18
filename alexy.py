from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from settings import nrdt_server, nrdt_user, nrdt_password
import os

# Set parameters to start Chrome in headless mode
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1200")
chrome_options.add_argument("--headless")

# Using Chrome to access web
browser = webdriver.Chrome()
browser.get(nrdt_server)

# Fill login form
username_box = browser.find_element(By.ID, 'email')
username_box.send_keys(nrdt_user)
password_box = browser.find_element(By.ID, 'passwd')
password_box.send_keys(nrdt_password)

# Click login
login_btn = browser.find_element(By.ID, 'login')
login_btn.click()

# close the alert pop-up after login
browser.switch_to.alert.accept()


def network_config_view_host(target_host):
    # open file
    outfile = open('hosts_scraping.txt', 'a')

    # select Network Config tab
    net_config_btn = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Network Config')))

    # click network config
    net_config_btn.click()

    # Select the Host name box
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'text')))
    browser.find_element(By.ID, 'text').clear()
    host_box = browser.find_element(By.ID, 'text')
    host_box.send_keys(target_host)

    # click filter button
    filter_btn = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "btnFilter")))
    filter_btn.click()

    try:
        target_btn = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id,'jqg_ip-address-host-list')]")))
        target_btn.click()

        open_host_btn = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "btnOpenIPAddressHost")))
        open_host_btn.click()

        shelf_link = browser.find_element(By.ID, 'hostDesignShelf')
        shelf_link.click()

        page_html = browser.page_source
        soup = BeautifulSoup(page_html, features="html.parser")

        # click to configure
        configure_cards = browser.find_elements(By.CLASS_NAME, 'configureItem')
        card_ids = [card.get_attribute("data-itemid") for card in configure_cards]
        data_list = []
        outfile.write("\n" + target_host + "\n")

        while len(card_ids) > 0:
            card_id = card_ids.pop(0)
            xpath = "//input[@data-itemid='" + card_id + "']"
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            browser.find_element(By.XPATH, xpath).click()
            page_html = browser.page_source
            soup = BeautifulSoup(page_html, features="html.parser")
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "designerDiv")))
            card_heading = browser.find_element(By.XPATH, '//*[@id="designerDiv"]/h2[1]/a')
            outfile.write("\t" + card_heading.text + ':\n')
            all_ports = soup.find_all("div", {"class": "port-item"})
            for port in all_ports:
                if port is not None:
                    try:
                        port_label = port.find('strong').getText(strip=True)
                        port_relationship = port.find("div", {"class": "port-relationship"}).getText(strip=True)
                        print("\n" + port_label + "\t" + port_relationship + "\n\n")
                        outfile.write("\n" + port_label + "\t" + port_relationship + "\n\n")
                    except Exception as err:
                        print(err)
                else:
                    print("Port is empty")

            items = soup.find_all("div", {"class": "item"})
            for item in items:
                for header in item.find_all('div'):
                    if header is not None:
                        try:
                            header_label = header.find('strong').getText(strip=True)
                            header_type = header.find('a').getText(strip=True)
                            header_info = header.find('span').getText(strip=True)
                            data_list.append("\n" + header_label + "\t" + header_type + "\t" + header_info + "\n\n")
                        except Exception as err:
                            print(err)
                    else:
                        print("Header is empty")

            subports = soup.find_all("div", {"class": "sub-port-item"})
            for subport in subports:
                if subport is not None:
                    try:
                        subport_label = subport.find('strong').getText(strip=True)
                        subport_relationship = subport.find("div", {"class": "port-relationship"}).getText(strip=True)
                        list_element = data_list.pop(0)
                        outfile.write(list_element)
                        outfile.write("Ports: " + subport_label + "\n" + subport_relationship + "\n\n")
                    except Exception as err:
                        print(err)
                else:
                    print("Subport is empty")

            browser.back()

    except (NoSuchElementException, TimeoutException):
        outfile.write("\n" + target_host + "  not found \n")
        outfile.write("\n-----------------------------------\n")
        outfile.close()

    except Exception as err:
        print("Exception? \n", err)

    outfile.close()


target_hosts = ["ashs-sbam-01", "MSCS-ACCR-01"]

for target_host in target_hosts:
    network_config_view_host(target_host)

browser.quit()
