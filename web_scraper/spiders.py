import re
from typing import Generator, Any, Dict, Optional, List

from scrapy import Spider, Request
from scrapy.http import Response

from .public_transport import PublicTransport

IRELAND_AREA = "ireland"

PAGE_SIZE = 'pageSize'

DUBLIN_CITY_SECTOR = 'Dublin City'

BER_RATING_EXEMPT_CODE = 'SI_666'
BER_RATING_EXEMPT = None

PROPERTY_CARD_SELECTOR = 'li[data-testid^="result"] > a::attr(href)'

DAFT_ADDRESS = "https://www.daft.ie"
PROPERTIES_FOR_SALE = "/property-for-sale"

PROPERTY_TYPE_SELECTOR = 'p[data-testid="property-type"]::text'
MAIN_ADDRESS_SELECTOR = 'h1[data-testid="address"]::text'
BER_RATING_ALT_SELECTOR = 'div[data-testid="ber"] > img::attr(alt)'
PRICE_SELECTOR = 'div[data-testid="price"] > p > span::text'
BEDS_SELECTOR = 'p[data-testid="beds"]::text'
BATHS_SELECTOR = 'p[data-testid="baths"]::text'
FLOOR_AREA_SELECTOR = 'p[data-testid="floor-area"]::text'
STREET_VIEW_SELECTOR = 'a[data-testid="streetview-button"]::attr(href)'
DESCRIPTION_SELECTOR = 'div[data-testid="description"]::text'
STATISTICS_SELECTOR = 'div[data-testid="statistics"] > div > div > div > p::text'

DEFAULT_PAGE_SIZE = 20


class DaftSaleUsedSpider(Spider):  # type: ignore
    name = "DaftSaleUsed"

    def __init__(self,
                 locations: List[str] = None,
                 min_price: Optional[int] = None,
                 max_price: Optional[int] = None,
                 min_beds: Optional[int] = None,
                 max_beds: Optional[int] = None,
                 ) -> None:
        super(DaftSaleUsedSpider, self).__init__()

        initial_url = DAFT_ADDRESS + PROPERTIES_FOR_SALE

        url_args = "?"
        initial_location = IRELAND_AREA
        if not locations:
            pass
        elif len(locations) < 2:
            if len(locations) == 1:
                initial_location = locations[0]
        else:
            for location in locations:
                url_args += DaftSaleUsedSpider._url_arg("location", location.strip())

        initial_url += f"/{initial_location}"
        self.base_url = initial_url

        url_args += DaftSaleUsedSpider._url_arg(PAGE_SIZE, DEFAULT_PAGE_SIZE)
        url_args += DaftSaleUsedSpider._url_arg('salePrice_from', min_price)
        url_args += DaftSaleUsedSpider._url_arg('salePrice_to', max_price)
        url_args += DaftSaleUsedSpider._url_arg('numBeds_from', min_beds)
        url_args += DaftSaleUsedSpider._url_arg('numBeds_to', max_beds)
        self.base_url_args = url_args
        self.start_from = 0

        url_args += DaftSaleUsedSpider._url_arg('from', self.start_from)

        self.start_urls = [self.base_url + url_args]
        print(f"Defined start url as: '{self.start_urls}'")

    def parse(self, response: Response) -> Generator[Request, None, None]:
        properties_response = response.css(PROPERTY_CARD_SELECTOR)
        for daft_property in properties_response:
            partial_url = daft_property.get()
            detailed_link = DAFT_ADDRESS + partial_url
            yield Request(detailed_link, callback=self.parse_detailed_page)

        if properties_response:
            self.start_from += DEFAULT_PAGE_SIZE
            next_page_url = self.base_url + self.base_url_args + DaftSaleUsedSpider._url_arg("from", self.start_from)
            yield Request(next_page_url, callback=self.parse)

    def parse_detailed_page(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        geolocation_coords = DaftExtractor.extract_geolocation(response)

        yield {
            'link': response.request.url,
            'property_type': DaftExtractor.extract_property_type(response),
            'ber_rating': DaftExtractor.extract_ber_rating(response),
            'price': DaftExtractor.extract_price(response),
            'bedrooms': DaftExtractor.extract_bedrooms(response),
            'bathrooms': DaftExtractor.extract_bathrooms(response),
            'floor_area_m2': DaftExtractor.extract_floor_area(response),
            'main_address': DaftExtractor.extract_main_address(response),
            'sector': DaftExtractor.extract_sector(response),
            'region': DaftExtractor.extract_region(response),
            'geolocation': geolocation_coords,
            'description': DaftExtractor.extract_description(response),
            'updated_at': DaftExtractor.extract_updated_at(response),
            'views': DaftExtractor.extract_views(response),
            'green_luas_distance_m': PublicTransport.get_closest_green_luas(geolocation_coords)[1],
            'red_luas_distance_m': PublicTransport.get_closest_red_luas(geolocation_coords)[1],
            'dart_distance_m': PublicTransport.get_closest_dart(geolocation_coords)[1],
        }

    @staticmethod
    def _url_arg(arg_name: str, arg_value: Any) -> str:
        if arg_value:
            return f'{arg_name}={arg_value}&'
        else:
            return ''


class DaftExtractor:
    _ber_rating_regex = re.compile("^.*/\\w+_(\\w+)\\..*$")
    _price_replace_regex = re.compile("[^\\d]")
    _quick_details_regex = re.compile("^Number.* (\\w+) is .*(\\d+)$")
    _FLOOR_AREA_REGEX = re.compile(".*\\s+(\\d+(\\.\\d+)?).* m")
    _UPDATED_AT_REGEX = re.compile("^(\\d{1,2}).(\\d{1,2}).(\\d{4})$")
    _ONLY_NUMBERS_REGEX = re.compile("^(\\d+,)?\\d+$")

    @staticmethod
    def extract_property_type(response: Response) -> str:
        result = str(DaftExtractor._extract_css_selector(response, PROPERTY_TYPE_SELECTOR))
        return result.strip()

    @staticmethod
    def extract_ber_rating(response: Response) -> Optional[str]:
        ber_rating = str(DaftExtractor._extract_css_selector(
            response, BER_RATING_ALT_SELECTOR))

        if ber_rating == BER_RATING_EXEMPT_CODE:
            return None

        return ber_rating

    @staticmethod
    def extract_price(response: Response) -> Optional[int]:
        price_text = str(DaftExtractor._extract_css_selector(response, PRICE_SELECTOR))
        result = None
        if price_text:
            try:
                result = int(DaftExtractor._price_replace_regex.sub("", price_text))
            except ValueError as e:
                if price_text.strip() and 'APPLICATION' not in price_text.upper():
                    raise ExtractorException('Error parsing price', price_text, e)
        return result

    @staticmethod
    def extract_bedrooms(response: Response) -> Optional[int]:
        return DaftExtractor.extract_first_int(response, BEDS_SELECTOR, 'beds')

    @staticmethod
    def extract_bathrooms(response: Response) -> Optional[int]:
        return DaftExtractor.extract_first_int(response, BATHS_SELECTOR, 'baths')

    @staticmethod
    def extract_floor_area(response: Response) -> Optional[float]:
        return DaftExtractor.extract_first_float(response, FLOOR_AREA_SELECTOR, 'floor-area')

    @staticmethod
    def extract_main_address(response: Response) -> str:
        result = str(DaftExtractor._extract_css_selector(response, MAIN_ADDRESS_SELECTOR))
        return result.strip()

    @staticmethod
    def extract_sector(response: Response) -> Optional[str]:
        main_address_parts = str(DaftExtractor._extract_css_selector(
            response, MAIN_ADDRESS_SELECTOR)).split(',')
        result = None
        if len(main_address_parts) > 1:
            result = main_address_parts[-1].strip()
        return result

    @staticmethod
    def extract_region(response: Response) -> Optional[str]:
        main_address_parts = str(DaftExtractor._extract_css_selector(
            response, MAIN_ADDRESS_SELECTOR)).split(',')
        result = None
        if len(main_address_parts) > 2 and DUBLIN_CITY_SECTOR in main_address_parts[-1]:
            result = main_address_parts[-3].strip()
        elif len(main_address_parts) > 2:
            result = main_address_parts[-2].strip()
        return result

    @staticmethod
    def extract_geolocation(response: Response) -> Optional[str]:
        street_view_link = DaftExtractor._extract_css_selector(response, STREET_VIEW_SELECTOR)
        result = None
        if street_view_link:
            raw_coordinates = street_view_link.split('=')[-1]
            result = raw_coordinates
        return result

    @staticmethod
    def extract_description(response: Response) -> str:
        description_text = DaftExtractor._extract_css_selector(response, DESCRIPTION_SELECTOR, True)
        result = ""
        for line in description_text:
            if line_text := line.strip():
                result += line_text + " "
        return result.strip()

    @staticmethod
    def extract_updated_at(response: Response) -> Optional[str]:
        statistics_raw = DaftExtractor._extract_css_selector(response, STATISTICS_SELECTOR, True)
        updated_at = None
        for statistics_entry in statistics_raw:
            if matcher := DaftExtractor._UPDATED_AT_REGEX.match(statistics_entry):
                updated_at = matcher.group(3) + '-' + matcher.group(2) + '-' + matcher.group(1)
                break
        return updated_at

    @staticmethod
    def extract_views(response: Response) -> Optional[int]:
        statistics_raw = DaftExtractor._extract_css_selector(response, STATISTICS_SELECTOR, True)
        views = None
        for statistics_entry in statistics_raw:
            if DaftExtractor._ONLY_NUMBERS_REGEX.match(statistics_entry):
                statistics_entry = statistics_entry.replace(",", "")
                views = int(statistics_entry)
                break
        return views

    @staticmethod
    def _extract_css_selector(response: Response, selector: str, get_all: bool = False) -> Any:
        if not get_all:
            return response.css(selector).get()
        else:
            return response.css(selector).getall()

    @staticmethod
    def extract_first_int(response: Response, selector: str, name: str) -> Optional[int]:
        property_text = DaftExtractor._extract_css_selector(response, selector)
        result = None
        if property_text:
            try:
                result = int(property_text.split(' ')[0])
            except ValueError as e:
                raise ExtractorException(f'Error parsing {name}', property_text, e)

        return result

    @staticmethod
    def extract_first_float(response: Response, selector: str, name: str) -> Optional[float]:
        property_text = DaftExtractor._extract_css_selector(response, selector)
        result = None
        if property_text:
            try:
                result = float(property_text.split(' ')[0])
            except ValueError as e:
                raise ExtractorException(f'Error parsing {name}', property_text, e)

        return result


class ExtractorException(Exception):
    def __init__(self, error_msg: str, raw_value: str, error: Any):
        self.message = f'{error_msg}:\'{raw_value}\' - {error}'

    def __str__(self) -> str:
        return self.message
