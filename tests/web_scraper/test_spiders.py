from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest
from scrapy.http import Response

from web_scraper.spiders import DaftSaleUsedSpider, DAFT_ADDRESS, DUBLIN_CITY, PROPERTIES_FOR_SALE, \
    PROPERTY_CARD_SELECTOR, LINK_SELECTOR, DaftExtractor, PROPERTY_TYPE_SELECTOR, PRICE_SELECTOR, \
    ExtractorException, FLOOR_AREA_SELECTOR, MAIN_ADDRESS_SELECTOR, STREET_VIEW_SELECTOR, \
    DESCRIPTION_SELECTOR, STATISTICS_SELECTOR, NEXT_PAGE_SELECTOR, BER_RATING_ALT_SELECTOR, BEDS_SELECTOR, \
    BATHS_SELECTOR

NEXT_PAGE_FULL_ADDRESS = 'NEXT_PAGE_FULL_ADDRESS'

NEXT_PAGE_ADDRESS = 'next_page'

PROPERTY_TYPE = 'Property type'
PROPERTY_TYPE_RAW = '\n            Property type\n    '

BER_RATING = 'A1'
BER_RATING_RAW_EXEMPT = 'SI_666'
BER_RATING_EXEMPT = None

PRICE_RAW = '€375,000'
PRICE = 375000
PRICE_BIG_RAW = '€2,750,000'
PRICE_BIG = 2750000
PRICE_NO_VALUE_RAW = '\n'
PRICE_NO_VALUE = None
PRICE_INVALID = None
PRICE_INVALID_RAW = 'INVALID'
PRICE_ON_APPLICATION_RAW = 'Price On Application'
PRICE_INVALID_EXCEPTION_MSG = r"Error .*pars.*price.*:'INVALID'"

BEDROOMS_RAW = '3 Bed'
BATHROOMS_RAW = '2 Bath'
BEDROOMS = 3
BEDROOMS_NO_VALUE = None
BATHROOMS = 2
BATHROOMS_NO_VALUE = None

FLOOR_AREA_RAW = '54 m²'
FLOOR_AREA = 54
FLOOR_AREA_DECIMAL_RAW = '50.3 m²'
FLOOR_AREA_DECIMAL = 50.3

MAIN_ADDRESS_RAW = "Apartment 12, Stewart Hall, Ryder's Row, Dublin 1, Dublin City Centre"
MAIN_ADDRESS = "Apartment 12, Stewart Hall, Ryder's Row, Dublin 1, Dublin City Centre"
MAIN_ADDRESS_SINGLE_RAW = 'SingleAdress'
MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE = '7 Crofton Terrace, Dun Laoghaire, South Co. Dublin'
MAIN_ADDRESS_NO_DISTRICT_MALAHIDE = '44 The Walk, Robswalls, Malahide, North Co. Dublin'
MAIN_ADDRESS_SECTOR = 'Dublin City Centre'
MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE_SECTOR = 'South Co. Dublin'
MAIN_ADDRESS_NO_DISTRICT_MALAHIDE_SECTOR = 'North Co. Dublin'
MAIN_ADDRESS_DISTRICT = 'Dublin 1'
MAIN_ADDRESS_REGION = "Ryder's Row"
MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE_REGION = 'Dun Laoghaire'
MAIN_ADDRESS_NO_DISTRICT_MALAHIDE_REGION = 'Malahide'

EIR_CODE_RAW = ['\n                            ', ' D04\xa0TD53\n                        ']
EIR_CODE = 'D04-TD53'
EIR_CODE_NO_VALUE_RAW = []
EIR_CODE_NO_VALUE = None

GEOLOCATION_RAW = 'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=53.329523,-6.278734'
GEOLOCATION = '53.329523,-6.278734'

DESCRIPTION_RAW = ["\n                         A wonderful opportunity ", '\n',
                   '\nThis attractive double ', ", Palmerston Park, local ",
                   '\nSide entrance\n                    ',
                   'Make it stand out and get up to 15x more views']
DESCRIPTION = "A wonderful opportunity This attractive double , Palmerston Park," \
              " local Side entrance Make it stand out and get up to 15x more views"

STATISTICS_RAW = ['19.04.2020', '2914']
UPDATED_AT = '2020-04-19'
VIEWS = 2914

URL = 'url'

FULL_LINK_2 = 'http://site.com/link_2'

FULL_LINK_1 = 'http://site.com/link_1'

SHORT_LINK_1 = 'link_1'
SHORT_LINK_2 = 'link_2'

INITIAL_URL = DAFT_ADDRESS + DUBLIN_CITY + PROPERTIES_FOR_SALE
INITIAL_ARGS = "/?ad_type=sale"
INITIAL_AREAS = "dublin-2,dublin-3"
MIN_PRICE = 1000
MAX_PRICE = 1000000
MIN_AND_MAX_PRICE_URL = '&s%5Bmnp%5D=1000&s%5Bmxp%5D=1000000'
MIN_BEDS = 2
MAX_BEDS = 4
MIN_AND_MAX_BEDS_URL = '&s%5Bmnb%5D=2&s%5Bmxb%5D=4'


@pytest.fixture
def daft_sale_used():
    return DaftSaleUsedSpider()


@pytest.fixture
def response():
    result = Response(URL)
    result.request = Response(URL)
    return result


@pytest.mark.parametrize("spider, expected_start_url", [
    (DaftSaleUsedSpider(),
     INITIAL_URL + INITIAL_ARGS),
    (DaftSaleUsedSpider(areas_string=INITIAL_AREAS),
     INITIAL_URL + "/" + INITIAL_AREAS + INITIAL_ARGS),
    (DaftSaleUsedSpider(min_price=MIN_PRICE, max_price=MAX_PRICE),
     INITIAL_URL + INITIAL_ARGS + MIN_AND_MAX_PRICE_URL),
    (DaftSaleUsedSpider(areas_string=INITIAL_AREAS, min_price=MIN_PRICE, max_price=MAX_PRICE),
     INITIAL_URL + "/" + INITIAL_AREAS + INITIAL_ARGS + MIN_AND_MAX_PRICE_URL),
    (DaftSaleUsedSpider(areas_string=INITIAL_AREAS, min_beds=MIN_BEDS, max_beds=MAX_BEDS),
     INITIAL_URL + "/" + INITIAL_AREAS + INITIAL_ARGS + MIN_AND_MAX_BEDS_URL),
])
def test_daft_sale_used_spider_init(spider, expected_start_url):
    assert spider.start_urls == [expected_start_url]


@patch('web_scraper.spiders.Request')
def test_daft_sale_should_parse_property_cards(request_mock, daft_sale_used):
    mock_list_response = MagicMock()
    property1 = _generate_response_for_css_selector(SHORT_LINK_1)
    property2 = _generate_response_for_css_selector(SHORT_LINK_2)
    next_page_css = MagicMock()
    next_page_css.get.return_value = None

    mock_list_response.css.side_effect = [[property1, property2], next_page_css]
    mock_list_response.urljoin.side_effect = [FULL_LINK_1, FULL_LINK_2]

    detailed_request_generator = daft_sale_used.parse(mock_list_response)

    results = [value for value in detailed_request_generator]
    assert len(results) == 2

    mock_list_response.css.assert_has_calls(
        [call(PROPERTY_CARD_SELECTOR), call(NEXT_PAGE_SELECTOR)])
    property1.css.assert_called_once_with(LINK_SELECTOR)
    property2.css.assert_called_once_with(LINK_SELECTOR)

    mock_list_response.urljoin.assert_has_calls([call(SHORT_LINK_1), call(SHORT_LINK_2)])

    request_mock.assert_has_calls([call(FULL_LINK_1, callback=daft_sale_used.parse_detailed_page),
                                   call(FULL_LINK_2, callback=daft_sale_used.parse_detailed_page)])


@patch('web_scraper.spiders.Request')
def test_daft_sale_should_try_to_parse_next_page(request_mock, daft_sale_used):
    mock_list_response = MagicMock()
    next_page_css = MagicMock()
    next_page_css.get.return_value = NEXT_PAGE_ADDRESS
    mock_list_response.css.side_effect = [[], next_page_css]
    mock_list_response.urljoin.side_effect = [NEXT_PAGE_FULL_ADDRESS]

    detailed_request_generator = daft_sale_used.parse(mock_list_response)
    results = [value for value in detailed_request_generator]

    mock_list_response.css.assert_has_calls(
        [call(PROPERTY_CARD_SELECTOR), call(NEXT_PAGE_SELECTOR)])
    mock_list_response.urljoin.assert_has_calls([call(NEXT_PAGE_ADDRESS)])
    request_mock.assert_called_once_with(NEXT_PAGE_FULL_ADDRESS, callback=daft_sale_used.parse)


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_property_link(extractor, daft_sale_used, response):
    data_generator = daft_sale_used.parse_detailed_page(response)

    results = [value for value in data_generator]

    assert len(results) == 1
    assert results[0]['link'] == 'url'


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_property_type(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_property_type,
                             PROPERTY_TYPE, 'property_type')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_ber_rating(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_ber_rating,
                             BER_RATING, 'ber_rating')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_price(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_price,
                             PRICE, 'price')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_bedrooms(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_bedrooms,
                             BEDROOMS, 'bedrooms')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_bathrooms(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_bathrooms,
                             BATHROOMS, 'bathrooms')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_floor_area(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_floor_area,
                             FLOOR_AREA, 'floor_area_m2')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_main_address(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_main_address,
                             MAIN_ADDRESS, 'main_address')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_sector(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_sector,
                             MAIN_ADDRESS_SECTOR, 'sector')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_region(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_region,
                             MAIN_ADDRESS_DISTRICT, 'region')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_geolocation(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_geolocation,
                             GEOLOCATION, 'geolocation')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_description(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_description,
                             DESCRIPTION, 'description')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_updated_at(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_updated_at,
                             UPDATED_AT, 'updated_at')


@patch('web_scraper.spiders.DaftExtractor')
def test_daft_sale_should_parse_the_views(extractor, daft_sale_used, response):
    _assert_extractor_called(daft_sale_used, response, extractor.extract_views,
                             VIEWS, 'views')


def test_daft_extractor_should_extract_property_type():
    _assert_parsed_by_extractor(DaftExtractor.extract_property_type, PROPERTY_TYPE_SELECTOR,
                                PROPERTY_TYPE_RAW, PROPERTY_TYPE)


@pytest.mark.parametrize('raw_value, expected_value', [
    (BER_RATING, BER_RATING),
    (BER_RATING_RAW_EXEMPT, BER_RATING_EXEMPT),
])
def test_daft_extractor_should_extract_ber_rating(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_ber_rating,
                                BER_RATING_ALT_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value, exception_msg', [
    (PRICE_RAW, PRICE, None),
    (PRICE_BIG_RAW, PRICE_BIG, None),
    (PRICE_NO_VALUE_RAW, PRICE_NO_VALUE, None),
    (PRICE_ON_APPLICATION_RAW, PRICE_NO_VALUE, None),
    (PRICE_INVALID_RAW, PRICE_INVALID, PRICE_INVALID_EXCEPTION_MSG),
])
def test_daft_extractor_should_extract_price(raw_value, expected_value, exception_msg):
    _assert_parsed_by_extractor(DaftExtractor.extract_price,
                                PRICE_SELECTOR, raw_value, expected_value, exception_msg)


@pytest.mark.parametrize('raw_value, expected_value', [
    (BEDROOMS_RAW, BEDROOMS),
    (None, BEDROOMS_NO_VALUE)
])
def test_daft_extractor_should_extract_bed_rooms(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_bedrooms,
                                BEDS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (BATHROOMS_RAW, BATHROOMS),
    (None, BATHROOMS_NO_VALUE),
])
def test_daft_extractor_should_extract_bath_rooms(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_bathrooms,
                                BATHS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (FLOOR_AREA_RAW, FLOOR_AREA),
    (FLOOR_AREA_DECIMAL_RAW, FLOOR_AREA_DECIMAL),
])
def test_daft_extractor_should_extract_floor_area(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_floor_area,
                                FLOOR_AREA_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (MAIN_ADDRESS_RAW, MAIN_ADDRESS),
    (MAIN_ADDRESS_SINGLE_RAW, MAIN_ADDRESS_SINGLE_RAW),
])
def test_daft_extractor_should_extract_main_address(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_main_address,
                                MAIN_ADDRESS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (MAIN_ADDRESS_RAW, MAIN_ADDRESS_SECTOR),
    (MAIN_ADDRESS_SINGLE_RAW, None),
    (MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE, MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE_SECTOR),
    (MAIN_ADDRESS_NO_DISTRICT_MALAHIDE, MAIN_ADDRESS_NO_DISTRICT_MALAHIDE_SECTOR),
])
def test_daft_extractor_should_extract_sector(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_sector,
                                MAIN_ADDRESS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (MAIN_ADDRESS_RAW, MAIN_ADDRESS_REGION),
    (MAIN_ADDRESS_SINGLE_RAW, None),
    (MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE, MAIN_ADDRESS_NO_DISTRICT_DUN_LAOGHAIRE_REGION),
    (MAIN_ADDRESS_NO_DISTRICT_MALAHIDE, MAIN_ADDRESS_NO_DISTRICT_MALAHIDE_REGION),
])
def test_daft_extractor_should_extract_region(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_region,
                                MAIN_ADDRESS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (GEOLOCATION_RAW, GEOLOCATION),
])
def test_daft_extractor_should_extract_geolocation(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_geolocation,
                                STREET_VIEW_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (DESCRIPTION_RAW, DESCRIPTION),
])
def test_daft_extractor_should_extract_description(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_description,
                                DESCRIPTION_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (STATISTICS_RAW, UPDATED_AT),
])
def test_daft_extractor_should_extract_updated_at(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_updated_at,
                                STATISTICS_SELECTOR, raw_value, expected_value)


@pytest.mark.parametrize('raw_value, expected_value', [
    (STATISTICS_RAW, VIEWS),
])
def test_daft_extractor_should_extract_views(raw_value, expected_value):
    _assert_parsed_by_extractor(DaftExtractor.extract_views,
                                STATISTICS_SELECTOR, raw_value, expected_value)


def _generate_response_for_css_selector(result: Any):
    response = MagicMock(Response)
    css_result = MagicMock()

    css_result.get.return_value = result
    css_result.getall.return_value = result
    response.css.return_value = css_result

    return response


def _assert_extractor_called(daft_sale_used, response, extractor_function, extractor_result,
                             property_name) -> None:
    extractor_function.side_effect = [extractor_result]
    data_generator = daft_sale_used.parse_detailed_page(response)

    results = [value for value in data_generator]

    assert len(results) == 1
    assert results[0][property_name] == extractor_result

    extractor_function.assert_called_once_with(response)


def _assert_parsed_by_extractor(extractor, selector, raw_value, expected_value,
                                expected_exception_regex=None):
    response = _generate_response_for_css_selector(raw_value)

    if not expected_exception_regex:
        result = extractor(response)
        assert result == expected_value
    else:
        with pytest.raises(ExtractorException, match=expected_exception_regex):
            extractor(response)

    response.css.assert_called_once_with(selector)
