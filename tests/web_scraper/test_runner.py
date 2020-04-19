from unittest import mock
from unittest.mock import Mock

import pytest

from web_scraper.runner import USER_AGENT_SETTING, DEFAULT_AREAS
from web_scraper.spiders import DaftSaleUsedSpider
from web_scraper import Runner, WebSources

AREAS_TO_LOOK = 'areas_to_look'


@pytest.fixture()
def runner():
    result = Runner()
    result._process = Mock()
    return result


@pytest.mark.parametrize('name, value', [('HOUSES_FOR_SALE', 'houses_for_sale'),
                                         ('HOUSES_FOR_RENT', 'houses_for_rent')])
def test_web_sources_should_return_the_value_in_str(name, value):
    assert str(WebSources[name]) == value


@mock.patch('web_scraper.runner.CrawlerProcess')
def test_crawler_should_run_with_provided_settings(crawler_process_mock):
    runner = Runner()
    crawler_process_mock.assert_called_once_with(settings=runner.crawler_settings)


def test_runner_should_parse_daft(runner):
    runner.run(runner.get_arg_parser().parse_args(args=['houses_for_sale']))
    runner._process.crawl.assert_called_once_with(DaftSaleUsedSpider, areas_string=DEFAULT_AREAS)
    runner._process.start.assert_called_once_with()


def test_runner_should_parse_daft_with_correct_areas(runner):
    runner.run(runner.get_arg_parser().parse_args(args=['houses_for_sale', '--areas-string',
                                                        AREAS_TO_LOOK]))
    runner._process.crawl.assert_called_once_with(DaftSaleUsedSpider, areas_string=AREAS_TO_LOOK)
    runner._process.start.assert_called_once_with()


def test_crawler_identify_it_self_as_google_bot(runner):
    assert 'Googlebot' in runner.crawler_settings[USER_AGENT_SETTING]
