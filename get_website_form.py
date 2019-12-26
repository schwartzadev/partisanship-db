import pandas as pd
import sys
from selenium import webdriver
import math
import json
import time


with open('user_info.json') as json_file:
	data = json.load(json_file)
	GMAIL_USERNAME = data['username']


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

	try:
		candidates['successful_registration']
	except KeyError as e:
		print('the specified dataframe does not have a column named "successful_registration"...adding one now')
		candidates.insert(5, 'successful_registration', None) # add column

	return candidates


def generate_email(campaign_id):
	return '{0}+{1}@gmail.com'.format(GMAIL_USERNAME, campaign_id)


candidates = check_arguments()

email_xpath = '//input[@type="email"]'


driver = webdriver.Firefox(executable_path=WEBDRIVER_PATH)


for index, row in candidates.tail(30).iterrows():
	if type(row['website']) is float and math.isnan(row['website']): # no website available
		continue
	if row['successful_registration'] is not None: # already documented
		continue

	driver.get(row['website'])

	try:
		email_fields = driver.find_elements_by_xpath(email_xpath)
		for field in email_fields:
			field.send_keys(generate_email(row['campaign_id']))
	except NoSuchElementException as e:
		print('no email inputs found...')

	print(row['name'], '...')
	print('    email:', generate_email(row['campaign_id']))
	# todo copy email to clipboard

	no_response = True
	while no_response:
		response = input('successful registration? (y/n) ')
		if response == 'y':
			# save and update database
			candidates.at[index, 'successful_registration'] = True
			no_response = False
		if response == 'n':
			# save and update db
			candidates.at[index, 'successful_registration'] = False
			no_response = False

	if index % 10 == 0 and index != 0:
		# update dataframe to file
		candidates.to_csv(
			'all_candidates_info_with_form_responses__{}__{}.csv'.format(index, time.strftime("%Y-%m-%d--%H-%M-%S"))
		)
		print('saved, index:', index)
