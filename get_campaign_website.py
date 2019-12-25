import get_all_candidates
import pdb
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sys
import time


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

	return candidates


def ballotpedia_search(candidate_name):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
		'DNT': '1',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
	}

	params = (
		('search', candidate_name),
	)

	response = requests.get('https://ballotpedia.org/wiki/index.php', headers=headers, params=params)

	soup = BeautifulSoup(response.content, 'html.parser')

	website_tag = soup.find('a', text=re.compile('Campaign website'))

	if website_tag is not None:
		return website_tag['href']
	return None


def add_website_column(candidates):
	try:
		candidates['website']
	except KeyError as e:
		# website column does not yet exist
		candidates.insert(3, 'website', '0')
		# note: '0' means a website hasn't been checked yet, None means no website has been found
	return candidates


candidates = check_arguments()

candidates = add_website_column(candidates) # adds a website column if one does not already exist

for index, row in candidates.iterrows():
	print('running', row['name'], '...')
	if row['website'] is not '0': # this website has already been ID'd
		continue
	website = ballotpedia_search(row['name'])
	candidates.at[index, 'website'] = website
	if index % 50 == 0 and index != 0:
		candidates.to_csv(
			'all_candidates_info_with_websites__{}.csv'.format(index)
		)
		print('saved, index:', index)


pdb.set_trace()
