import pandas as pd
import sys
from selenium import webdriver
import math


GMAIL_USERNAME = 'testtest'
WEBDRIVER_PATH = 'C:\\Users\\werdn\\Downloads\\geckodriver-v0.26.0-win64\\geckodriver.exe'


def check_arguments():
	if len(sys.argv) < 2:
		print('must specify a candidates csv filename as arg1...exiting')
		quit(99)

	candidates_filename = sys.argv[1]

	try:
		candidates = pd.read_csv(candidates_filename, index_col=0)
	except FileNotFoundError as e:
		print('the specified csv filename ({0}) does not exist...exiting'.format(candidates_filename))
		quit(99)

	try:
		candidates['website']
	except KeyError as e:
		print('the specified dataframe does not have a column named "website"...exiting')
		quit(99)

	return candidates


candidates = check_arguments()

email_xpath = '//input[@type="email"]'


driver = webdriver.Firefox(executable_path=WEBDRIVER_PATH)

for index, row in candidates.iterrows():
	# print('running', row['name'], '...')
	if type(row['website']) is float and math.isnan(row['website']): # no website available
		continue
	driver.get(row['website'])
	try:
		email_fields = driver.find_elements_by_xpath(email_xpath)
		for field in email_fields:
			field.send_keys(
				'{0}+{1}@gmail.com'.format(GMAIL_USERNAME, row['campaign_id'])
			)
	except NoSuchElementException as e:
		print('no email inputs found...')
	# todo handle operator feedback about successful registration
	import pdb
	pdb.set_trace()
