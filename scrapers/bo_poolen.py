# coding: utf-8
from urllib.request import urlopen
from bs4 import BeautifulSoup
from re import findall
import pickle
import logging, logging.handlers

#This variable is a regex which will match urls connected to this scraper
REGEX_PATTERN = r'.*bopoolen\.nu/.*'

#The actual scraper
class BoPoolenScraper():
	def __init__(self,url,upper_price):
		self.url = url
		self.ad_url_template = "http://bopoolen.nu/ad/landlord/{}/?lang=sv"
		self.ad_ids = []
		self.upper_price = upper_price

	def pickle_dump(self):
		with open('bo_poolen_pickle.txt','wb') as f:
			pickle.dump(self.ad_ids,f)
		logging.info('BoPoolen Pickle Dump')

	def pickle_load(self):
		with open('bo_poolen_pickle.txt','rb') as f:
			return pickle.load(f)

	def get_id(self,ad):
		return findall(r'ad-landlord-([0-9]+?)-ajax', ad.get('id'))[0]

	def get_title(self,ad):
		return ad.find_all('td')[1].text[:-19] #Removes 20 digit timestamp at end

	def get_price(self,ad):
		return int(ad.find_all('td')[-1].text)

	def get_date(self,ad):
		return ad.find_all('td')[1].text[-19:-9] #Gets the date from timestamp

	def get_link(self,ad):
		return self.ad_url_template.format(self.get_id(ad))

	def stringify(self,ad):
		return '{} \nPrice: {}\nDate: {}\nLink: {}\n'.format(self.get_title(ad),\
							self.get_price(ad),self.get_date(ad),self.get_link(ad))

	def scrape(self):
		self.ad_ids = self.pickle_load()
		with urlopen(self.url) as response:
			r = response.read()
		soup = BeautifulSoup(r, 'html.parser')
		ads = soup.find_all('tr',id = lambda x: x and x.startswith('ad-landlord-'))

		good_ads = [self.stringify(ad) for ad in ads if self.get_price(ad) < \
					self.upper_price and self.get_id(ad) not in self.ad_ids]

		for ad in ads:
			self.ad_ids.append(self.get_id(ad))

		return good_ads
