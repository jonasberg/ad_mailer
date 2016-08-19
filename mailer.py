# coding: utf-8
import private
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
	msg['To'] = private.YOU
	msg['From'] = private.ME

	#Connecting to gmail
	s = smtplib.SMTP(*private.MAILHOST)
	s.ehlo()
	s.starttls()
	s.ehlo
	s.login(private.G_USER,private.G_PW)
	logging.info('Connected to Gmail')

	#Sending
	s.sendmail(private.ME,[private.YOU],msg.as_string())
	logging.info('Mail Sent')
	s.quit()

	return True

def format_ad(ad):
	return '{title} \nPrice: {price}\nDate: {date}\nLink: {link}\n'.format(**ad)
