#Import all files containing scrapers
from re import match
from . import blocket
from . import bo_poolen

url_mapper = {
    blocket.REGEX_PATTERN: blocket.BlocketScraper,
    bo_poolen.REGEX_PATTERN: bo_poolen.BoPoolenScraper
}

def get_scraper(url):
    for pattern in url_mapper.keys():
        if match(pattern,url):
            return url_mapper[pattern]
