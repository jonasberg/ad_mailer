# coding: utf-8
import logging, logging.handlers
from urllib.request import urlopen
from bs4 import BeautifulSoup
from os.path import dirname,join
from re import compile

#This variable is a regex which will match urls connected to this scraper
REGEX_PATTERN = r'https?://(?:www|mobil)\.blocket\.se/.*'

#The actual scraper
class BlocketScraper():
	def __init__(self,url,**filters):
		self.url = url
		self.filters = filters
		self.ad_ids = []

	def dump_ids(self):
		file_url = join(dirname(__file__),"blocket_ids.txt")
		formatted_ads = map(lambda x: str(x)+"\n",self.ad_ids)

		with open(file_url,'a') as f:
			f.writelines(formatted_ads)
		self.ad_ids = []

		logging.info('Blocket Id Dump')

	def load_ids(self):
		file_url = join(dirname(__file__),"blocket_ids.txt")
		with open(file_url,'r') as f:
			return map(lambda x: x.replace("\n",""),f.readlines())

	def get_price(self,ad):
		if ad.find('span',{'class':'monthly_rent'}):
			text = ad.find('span',{'class':'monthly_rent'}).text
		elif ad.find('p', {'itemprop':'price'}):
			text = ad.find('p', {'itemprop':'price'}).text
		else:
			text = "0 kr"

		price = text.split(' kr')[0]
		price = price.replace(' ','') or 0 #If price doesn't exist
		return int(price)

	def get_id(self,ad):
		return ad.get('id')

	def is_good(self,ad):
		criterias = [
			self.get_id(ad) not in self.load_ids(),
			"max_price" in self.filters and self.get_price(ad) < self.filters["max_price"],
			"min_price" in self.filters and self.get_price(ad) > self.filters["min_price"]
		]

		return False not in criterias

	def parse(self,ad):
		return {
			'id' : self.get_id(ad),
			'title' : ad.find('a',{'class':'item_link'}).text.strip(),
			'link' : ad.find('a',{'class':'item_link'}).get('href'),
			'date' : ad.find('time').get('datetime'),
			'price' : self.get_price(ad)
		}

	def scrape(self):
		with urlopen(self.url) as response:
			r = response.read()
		soup = BeautifulSoup(r, 'html.parser')
		pattern = compile("item_[0-9]{8}")
		ads = soup.find_all(lambda tag: pattern.match(tag.get('id') or ""))
		parsed_ads = [self.parse(ad) for ad in ads if self.is_good(ad)]
		
		for ad in parsed_ads:
			self.ad_ids.append(self.get_id(ad))

		return parsed_ads
