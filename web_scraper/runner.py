from enum import Enum
from typing import Any

from scrapy import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response


class WebSources(Enum):
    __order__ = 'DAFT MY_HOME'
    DAFT = 'daft'
    MY_HOME = 'my_home'

    def __str__(self) -> str:
        return str(self.value)


class MySpider(Spider):  # type: ignore
    name = "my-spider"

    def __init__(self, my_arg: str = '', my_arg2: str = '') -> None:
        super(MySpider, self).__init__()
        print(f'my_arg: {my_arg}, my_arg2: {my_arg2}')

    def parse(self, response: Response) -> None:
        pass


class Runner:
    def __init__(self) -> None:
        self._process = CrawlerProcess()

    def run(self, args: Any) -> None:
        print("Hello world in Runner!")
        self._process.crawl(MySpider, my_arg='my_arg')
        self._process.start()
