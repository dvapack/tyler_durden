import json
import re
from bs4 import BeautifulSoup

class DataLoader:
    """
    Класс для загрузки json с данными о сохраненных рилсах.
    """
    def __init__(self, filepath: str):
        """
        :param filepath: Путь до файла. Либо до изначального saved_posts.json, либо до links.json
        """
        self.filepath = filepath
        self.links = []

    def initial_load_reels(self):
        """
        Метод для загрузки рилсов из json.
        """
        try:
            with open(self.filepath, 'r') as file:
                html_file = file.read()
                soup = BeautifulSoup(html_file, 'html.parser')

                data = {
                    "links": [{"text": a.get_text(strip=True), "href": a.get('href')}
                             for a in soup.find_all('a', href=True)],
                }
            print(data)
            reels = data["links"]
            for reel in reels:
                self.links.append(reel["href"].replace("www.", "d.dd"))
        except FileNotFoundError:
            print("Такого файла не существует")
        except KeyError:
            print("В json файле нет необходимых данных!")

    def load_links(self):
        """
        Метод для загрузки ссылок из json.
        """
        try:
            with open(self.filepath, 'r') as file:
                data = json.load(file)
            links = data["links"]
            for link in links:
                self.links.append(link)
        except FileNotFoundError:
            print("Такого файла не существует")
        except KeyError:
            print("В json файле нет необходимых данных!")


    def save_reels(self):
        """
        Метод для сохранения списка ссылок на рилсы в json файл.
        """
        with open('links.json', 'w') as file:
            json.dump({"links": self.links}, file)

    def get_reel(self) -> str:
        """
        Метод для получения ссылки на рилс.
        """
        try:
            link = self.links.pop()
            self.save_reels()
            return link
        except IndexError:
            print("Все рилсы скачаны!")
            return "Все рилсы скачаны!"
