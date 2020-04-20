import json
from unittest.mock import Mock, patch, mock_open

import pytest
from scrapy import Spider

from web_scraper.pipelines import JsonWriterPipeline


@pytest.fixture()
def json_writer_pipeline():
    return JsonWriterPipeline()


@pytest.fixture()
def item():
    return {'property': 'value'}


@pytest.fixture()
def spider():
    return Mock(Spider)


@pytest.fixture()
def json_writer_pipeline_with_item(item, spider):
    pipeline = JsonWriterPipeline()
    pipeline.process_item(item, spider)
    return pipeline


def test_init_has_empty_data(json_writer_pipeline):
    assert not json_writer_pipeline.data


def test_process_item_adds_to_data(json_writer_pipeline_with_item, item, spider):
    assert json_writer_pipeline_with_item.data == [item]


def test_open_spider_clears_data(json_writer_pipeline_with_item, spider):
    json_writer_pipeline_with_item.open_spider(spider)
    assert not json_writer_pipeline_with_item.data


def test_close_spider_saves_the_file(json_writer_pipeline_with_item, spider):
    open_mock = mock_open()

    with patch('web_scraper.pipelines.open', open_mock):
        json_writer_pipeline_with_item.close_spider(spider)

    open_mock.assert_called_once_with('/tmp/data.json', 'w')
    handle = open_mock()
    handle.write.assert_called_once_with(json.dumps(json_writer_pipeline_with_item.data))
