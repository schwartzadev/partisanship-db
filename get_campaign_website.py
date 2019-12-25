import get_all_candidates
import pdb
import requests
from bs4 import BeautifulSoup
import re


candidates = get_all_candidates.get_all_candidates()


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

	print(response.status_code)

	soup = BeautifulSoup(response.content, 'html.parser')
	website_tag = soup.find('a', text=re.compile('Campaign website'))
	if website_tag is not None:
		return website_tag['href']
	return None


def check_for_email_form(soup):
	return soup.find('form').find('input', {'type': 'email'}) is not None


for index, row in candidates.head(90).iterrows():
	print(ballotpedia_search(row['name']))


pdb.set_trace()
