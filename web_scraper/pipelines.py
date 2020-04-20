import json
from typing import Any, List

from scrapy import Spider


class JsonWriterPipeline:
    def __init__(self) -> None:
        self.data: List[Any] = []

    def open_spider(self, spider: Spider) -> None:
        self.data = []

    def close_spider(self, spider: Spider) -> None:
        with open('/tmp/data.json', 'w') as outfile:
            outfile.write(json.dumps(self.data))

    def process_item(self, item: Any, spider: Spider) -> Any:
        self.data.append(item)
        return item
