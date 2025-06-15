import requests
from bs4 import BeautifulSoup
import time


# 1. Простой запрос страницы
def get_page_html(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Проверка на ошибки HTTP

        # Проверяем, что получили HTML
        if 'text/html' not in response.headers['Content-Type']:
            raise ValueError("Ответ не является HTML")

        return response.text

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе страницы: {e}")
        return None


# 2. Сохранение HTML для анализа
def save_html(html, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"HTML сохранён в файл {filename}")
    except IOError as e:
        print(f"Ошибка при сохранении файла: {e}")


# 3. Основная функция
def main():
    url = "https://zvukogram.com/category/zvuki-avariy/"

    print(f"Пробуем получить страницу {url}...")
    start_time = time.time()

    html = get_page_html(url)
    if html:
        print("Успешно получили HTML!")
        print(f"Размер HTML: {len(html)} символов")

        # Сохраняем для анализа
        save_html(html, "zvukogram_page.html")

        # Простая проверка содержимого
        if "zvukogram" in html.lower():
            print("Сайт похож на zvukogram")
        else:
            print("Полученный HTML не содержит ожидаемого содержимого")

        # Можно быстро проверить заголовок
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else "Нет заголовка"
        print(f"Заголовок страницы: {title}")

    print(f"Время выполнения: {time.time() - start_time:.2f} секунд")


if __name__ == "__main__":
    main()