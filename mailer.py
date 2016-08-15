# coding: utf-8
from email.mime.text import MIMEText
from time import sleep
from os.path import basename
import smtplib
import pickle
import logging, logging.handlers
#import atexit

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
