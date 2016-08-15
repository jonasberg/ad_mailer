# coding: utf-8
from urllib.request import urlopen
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from time import sleep
from os.path import basename
from re import findall
import smtplib
import pickle
import logging, logging.handlers
#import atexit

class BlocketParser():
	def __init__(self,url,upper_price):
		self.url = url
		self.ad_ids = []
		self.upper_price = upper_price

	def pickle_dump(self):
		with open('blocket_gurka.txt','wb') as f:
			pickle.dump(self.ad_ids,f)
		logging.info('Blocket Pickle Dump')

	def pickle_load(self):
		with open('blocket_gurka.txt','rb') as f:
			return pickle.load(f)

	def get_price(self,ad):
		text = ad.find('span',{'class':'item_price'}).text
		price = text.split(' kr')[0]
		price = price.replace(' ','') or 0 #If price doesn't exist
		return int(price)

	def get_id(self,ad):
		return ad.get('id')

	def stringify(self,ad):
		title = ad.find('h2',{'class':'item_title'}).text
		link = ad.find('a',{'class':'item_link'}).get('href')
		date = ad.find('p',{'class':'item_date'}).text
		price = self.get_price(ad)

		return '{} \nPrice: {}\nDate: {}\nLink: {}\n'.format(title,price,date,link)

	def parse(self):
		self.ad_ids = self.pickle_load()

		with urlopen(self.url) as response:
			r = response.read()
		soup = BeautifulSoup(r, 'html.parser')
		ads = soup.find_all('li',{'class':'item'})
		good_ads = [self.stringify(ad) for ad in ads if self.get_price(ad) < self.upper_price and self.get_id(ad) not in self.ad_ids]

		for ad in ads:
			self.ad_ids.append(self.get_id(ad))

		return good_ads

class BoPoolenParser():
	def __init__(self,url,upper_price):
		self.url = url
		self.ad_url_template = "http://bopoolen.nu/ad/landlord/{}/?lang=sv"
		self.ad_ids = []
		self.upper_price = upper_price

	def pickle_dump(self):
		with open('bo_poolen_gurka.txt','wb') as f:
			pickle.dump(self.ad_ids,f)
		logging.info('BoPoolen Pickle Dump')

	def pickle_load(self):
		with open('bo_poolen_gurka.txt','rb') as f:
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

	def parse(self):
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

def send_mail(ads):
	#Params
	subject = '{} New Ads'.format(len(ads))
	contents = '\n'.join(ads)

	#Prepping email
	msg = MIMEText(contents)
	msg['Subject'] = subject
	msg['To'] = YOU
	msg['From'] = ME

	#Connecting to gmail
	s = smtplib.SMTP(*MAILHOST)
	s.ehlo()
	s.starttls()
	s.ehlo
	s.login(G_USER,G_PW)
	logging.info('Connected to Gmail')

	#Sending
	s.sendmail(ME,[YOU],msg.as_string())
	logging.info('Mail Sent')
	s.quit()

	return True

def main():
	logging.info('Initializing BlocketParser')
	blocket_url = 'http://mobil.blocket.se/bostad/uthyres/lagenheter/skane/lund'
	blocket = BlocketParser(blocket_url,4500)

	logging.info('Initializing BoPoolenParser')
	bo_poolen_url = 'http://bopoolen.nu/sokresultat/?lang=sv&ad-type=landlord&type%5B%5D=Room&type%5B%5D=Apartment&type%5B%5D=Couch&max_monthly_rent=4000&free_text=&submit=S%C3%B6k+annonser+%C2%BB#!prettyPhoto'
	bo_poolen = BoPoolenParser(bo_poolen_url,4500)

	logging.info('Starting Loop')
	while True:
		blocket_ads = blocket.parse()
		bo_poolen_ads = bo_poolen.parse()

		logging.info('{} Blocket ads found'.format(len(blocket_ads)))
		logging.info('{} Bo Poolen ads found'.format(len(bo_poolen_ads)))

		ads = blocket_ads + bo_poolen_ads

		if len(ads) != 0:
			if send_mail(ads): #Only dump if mail is actually sent
				blocket.pickle_dump()
				bo_poolen.pickle_dump()

		break
		logging.info('Hinernating for {} seconds'.format(str(SLEEP_SECONDS)))
		sleep(SLEEP_SECONDS)


if __name__ == '__main__':
	# SETTINGS
	SLEEP_SECONDS = 60

	#Mail settings
	MAILHOST = ('smtp.gmail.com', 587)
	ME = G_USER = 'python.o.matic@gmail.com'
	G_PW = 'pythonbot123'
	YOU = 'jonasberg@live.com'

	logging.getLogger().setLevel(logging.INFO)

	if not logging.StreamHandler in map(lambda h: h.__class__, logging.getLogger().handlers):
		logging.getLogger().addHandler(logging.StreamHandler())

	if not logging.handlers.SMTPHandler in map(lambda h: h.__class__, logging.getLogger().handlers):
		mail_handler = logging.handlers.SMTPHandler(MAILHOST,ME,[YOU],'Error running the script {}'.format(basename(__file__)),(G_USER,G_PW),tuple())
		mail_handler.setLevel(logging.WARNING)
		logging.getLogger().addHandler(mail_handler)

	try:
		main()

	except Exception as e:
		logging.error('Program crashed. Error message: \n\n{}'.format(str(e)))
