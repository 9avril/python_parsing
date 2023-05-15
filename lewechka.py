# Импортируем необходимые модули
import requests
from bs4 import BeautifulSoup
from html_data import html  # html_data - модуль, где хранится HTML код страницы

# Создаем объект BeautifulSoup, который будет парсить HTML код.
# Второй аргумент 'html.parser' указывает, что мы используем стандартный Python HTML парсер.
soup = BeautifulSoup(html, 'html.parser')

# Открываем файл output.txt в режиме записи. 'w' означает, что файл будет очищен, если он уже существует.
with open("output.txt", "w") as file:
    # Ищем все div-элементы, которые являются детьми элемента с id 'shelf-container'
    for row_div in soup.select('#shelf-container > div'):
        # Находим h2 элемент внутри div и получаем его текст, удаляя пробелы в начале и конце
        row = row_div.find('h2').text.strip()
        # Записываем строку в файл
        file.write(f"{row} ->\n")

        # Ищем все элементы с классом 'itemContainer' внутри div
        for item_container in row_div.select('.itemContainer'):
            # Проверяем, есть ли в списке классов элемента класс 'empty'
            if "empty" in item_container.get("class"):
                # Если есть, то записываем текст элемента в файл (это текст перед кнопкой "Add Card")
                un_equipped = item_container.contents[0].strip()
                file.write(f"{un_equipped}\n")
            else:
                # Если класса 'empty' нет, то считываем информацию о карте
                card_num = item_container.find(class_='itemHeader').strong.text.strip()  # номер карты
                card_name = item_container.find(class_='item-link').text.strip()  # название карты
                card_type = item_container.find_all('strong')[-1].next_sibling.strip()  # тип карты
                part_number = item_container.find(class_='itemDescription').strong.next_sibling.strip()  # номер партии

                # Записываем полученную информацию в файл
                line = f"{card_num} Card: {card_name}; Type: {card_type}; Part Number: {part_number};"
                file.write(f"{line}\n")

        # Добавляем пустую строку после каждого блока
        file.write("\n")
