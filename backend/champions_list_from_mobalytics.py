import requests
from bs4 import BeautifulSoup
import re


def clean_and_lowercase(s):
    # Удаление всех небуквенных знаков
    cleaned = re.sub("[^a-zA-Z]", "", s)
    # Приведение к прописному регистру
    return cleaned.lower()


def get_champion_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    champions = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "champions/" in href:
            champion_name = href.split("champions/")[-1]
            if champion_name:
                champion_name = clean_and_lowercase(champion_name)
                champions.append(champion_name)

    return champions
