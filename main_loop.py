# coding: utf-8
import settings
import scrapers
import mailer
from time import sleep
from os.path import basename
import logging, logging.handlers

def main():
	logging.info('Initializing Scrapers')
	initialized_scrapers = []
	for name, ad in settings.ads.items():
		try:
			scraperClass = scrapers.get_scraper(ad["url"])
		except ValueError as e:
			#If the url is not compatible with any scraper
			logging.warning(e)

		scraper = scraperClass(ad["url"],**ad["filters"])
		initialized_scrapers.append(scraper)

	logging.info('Starting Loop')
	while True:
		ads = []
		for scraper in initialized_scrapers:
			ads += scraper.scrape()

		if mailer.mail_ads(ads): #Only dump if mail is actually sent
			for scraper in initialized_scrapers:
				scraper.dump_ids()

		logging.info('Hinernating for {} seconds'.format(str(settings.SLEEP_SECONDS)))
		sleep(settings.SLEEP_SECONDS)


if __name__ == '__main__':
	logging.getLogger().setLevel(logging.INFO)

	if not logging.StreamHandler in map(lambda h: h.__class__, logging.getLogger().handlers):
		logging.getLogger().addHandler(logging.StreamHandler())

	#if not logging.handlers.SMTPHandler in map(lambda h: h.__class__, logging.getLogger().handlers):
	#	mail_handler = logging.handlers.SMTPHandler(MAILHOST,ME,[YOU],'Error running the script {}'.format(basename(__file__)),(G_USER,G_PW),tuple())
	#	mail_handler.setLevel(logging.WARNING)
	#	logging.getLogger().addHandler(mail_handler)

	try:
		main()

	except Exception as e:
		logging.error('Fatal error. Message: \n\n{}'.format(str(e)))
