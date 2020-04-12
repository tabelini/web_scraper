from scrapy import Spider
from scrapy.http import Response


class DaftSpider(Spider):  # type: ignore
    name = "my-spider"

    def __init__(self, my_arg: str = '', my_arg2: str = '') -> None:
        super(DaftSpider, self).__init__()
        print(f'my_arg: {my_arg}, my_arg2: {my_arg2}')

    def parse(self, response: Response) -> None:
        pass