import requests
from bs4 import BeautifulSoup


def get_champion_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    champions = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "champions/" in href:
            champion_name = href.split("champions/")[-1]
            if champion_name:  # Проверка на пустое значение
                champions.append(champion_name)

    return champions
