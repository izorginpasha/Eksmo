import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

base_url = "https://zvukogram.com"



def get_categories():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        categories = set()  # Используем множество для избежания дубликатов

        # Парсим категории из левого меню
        left_menu = soup.select_one('.leftSupermenu .lmenu')
        if left_menu:
            for item in left_menu.select('li a'):
                category_name = item.text.strip()
                category_url = urljoin(base_url, item['href'])
                categories.add((category_name, category_url))

        # Парсим категории из основного блока
        main_block = soup.select_one('.catlistmorda .superLi')
        if main_block:
            for item in main_block.select('li a'):
                category_name = item.text.strip()
                category_url = urljoin(base_url, item['href'])
                categories.add((category_name, category_url))

        # Преобразуем в список словарей и сортируем по имени
        sorted_categories = sorted([{'name': name, 'url': url} for name, url in categories],
                                   key=lambda x: x['name'])

        return sorted_categories

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе страницы: {e}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return []

def get_under_categoryes(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        categories = set()  # Используем множество для избежания дубликатов


        # Парсим под категории категории
        main_block = soup.select_one('.zvukcat ')
        if main_block:
            for item in main_block.select('li a'):
                category_name = item.text.strip()
                category_url = urljoin(base_url, item['href'])
                categories.add((category_name, category_url))

        # Преобразуем в список словарей и сортируем по имени
        sorted_categories = sorted([{'name': name, 'url': url} for name, url in categories],
                                   key=lambda x: x['name'])

        return sorted_categories

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе страницы: {e}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return []

def get_under_under_categoryes(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        categories = set()  # Используем множество для избежания дубликатов


        # Парсим под категории категории
        main_block = soup.select_one('.trackList ')
        if main_block:
            for item in main_block.select('.waveTitle'):
                category_name = item.text.strip()
                categories.add(category_name)

        # Преобразуем в список словарей и сортируем по имени
        sorted_categories = sorted([{'name': name} for name in categories],
                                   key=lambda x: x['name'])

        return sorted_categories

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе страницы: {e}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return []


def save_to_json(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Данные сохранены в {filename}")
    except IOError as e:
        print(f"Ошибка при сохранении файла: {e}")


if __name__ == "__main__":
    print("Начинаем парсинг категорий zvukogram.com...")
    categories = get_categories()
    under_categor = get_under_categoryes("https://zvukogram.com/category/avto/")
    under_under_categor = get_under_under_categoryes("https://zvukogram.com/category/zvuki-avariy/")

    if categories:
        print(f"Найдено {len(categories)} категорий:")
        for idx, category in enumerate(categories, 1):
            print(f"{idx}. {category['name']} - {category['url']}")

        save_to_json(categories, 'zvukogram_categories.json')
        save_to_json(under_categor, 'zvukogram_under_categor.json')
        save_to_json(under_under_categor, 'zvukogram_under_under_categor.json')
    else:
        print("Не удалось найти категории")
