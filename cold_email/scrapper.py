import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class BaseJobScrapper(ABC):
    @abstractmethod
    def extract(self, url):
        pass


class AppleJobScrapper(BaseJobScrapper):
    def __init__(self) -> None:
        self._target_tag = "span"

    def extract(self, url):
        page = requests.get(url).text
        soup = BeautifulSoup(page, "html.parser")
        item = soup.find_all(self._target_tag)

        page_content = ""
        for x in item:
            page_content += f" {x.get_text()}"

        page_title = soup.title.get_text()
        return page_title, page_content
