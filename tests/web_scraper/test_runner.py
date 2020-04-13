from unittest import mock
from unittest.mock import Mock, call

import pytest

from web_scraper.runner import USER_AGENT_SETTING
from web_scraper.spiders import DaftSaleUsedSpider
from web_scraper import Runner, WebSources


@pytest.fixture()
def runner():
    result = Runner()
    result._process = Mock()
    return result


@pytest.mark.parametrize('name, value', [('DAFT', 'daft'), ('MY_HOME', 'my_home')])
def test_web_sources_should_return_the_value_in_str(name, value):
    assert str(WebSources[name]) == value


@mock.patch('web_scraper.runner.CrawlerProcess')
def test_crawler_should_run_with_provided_settings(crawler_process_mock):
    runner = Runner()
    crawler_process_mock.assert_called_once_with(settings=runner.crawler_settings)


def test_runner_should_parse_daft_when_asked(runner):
    runner.run(runner.get_arg_parser().parse_args(args=['daft']))
    runner._process.crawl.assert_called_once_with(DaftSaleUsedSpider)
    runner._process.start.assert_called_once_with()


def test_crawler_identify_it_self_as_google_bot(runner):
    assert 'Googlebot' in runner.crawler_settings[USER_AGENT_SETTING]