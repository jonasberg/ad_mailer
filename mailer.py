# coding: utf-8
import settings
from email.mime.text import MIMEText
import smtplib
import logging, logging.handlers
#import atexit

def mail_ads(ads):
	if len(ads) == 0:
		return False

	#Params
	subject = '{} New Ads'.format(len(ads))
	contents = '\n'.join(map(format_ad,ads))

	#Prepping email
	msg = MIMEText(contents)
	msg['Subject'] = subject
	msg['To'] = settings.YOU
	msg['From'] = settings.ME

	#Connecting to gmail
	s = smtplib.SMTP(*settings.MAILHOST)
	s.ehlo()
	s.starttls()
	s.ehlo
	s.login(settings.G_USER,settings.G_PW)
	logging.info('Connected to Gmail')

	#Sending
	s.sendmail(settings.ME,[settings.YOU],msg.as_string())
	logging.info('Mail Sent')
	s.quit()

	return True

def format_ad(ad):
	return '{title} \nPrice: {price}\nDate: {date}\nLink: {link}\n'.format(**ad)
