# Web Scraper

## Description
Some toy tools to scrape some **irish** web sites and get some test data

## How to run it:
PYTHONPATH="PATH_TO_PROJECT/web_scraper:${PYTHONPATH}" python bin/web-scraper houses-for-sale --areas-string "dublin-4,dublin-6" --min-price 100000 --max-price 300000

houses-for-sale --areas-string "dublin-4,dublin-6" --min-price 100000 --max-price 300000

## How to run the tests:
PYTHONPATH="PATH_TO_PROJECT/web_scraper:${PYTHONPATH}" pytest -vv --cov=web_scraper

## Available Scrapers

### Houses for sale(houses_for_sale)

Scraps sites(only daft at the moment) for used houses for sale

#### Parameters:
* areas_string: areas that are being scraped as shown in daft.ie site.

Example: for the url https://www.daft.ie/dublin-city/houses-for-sale/dublin-1,dublin-4/?ad_type=sale&advanced=1&s%5Badvanced%5D=1&searchSource=sale,
areas string would be 'dublin-1,dublin-4'

