import pandas as pd
import sys
import selenium


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


def check_for_email_form(soup):
	return soup.find('form').find('input', {'type': 'email'}) is not None


candidates = check_arguments()

for index, row in candidates.iterrows():
	print('running', row['name'], '...')
	if row['website'] is None: # no website available
		continue
	# do checking, registering here

