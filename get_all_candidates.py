import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

"""
the filename should be a saved version of the wikipedia page below:
https://en.wikipedia.org/wiki/2020_United_States_House_of_Representatives_elections
"""
filename = "Wikipedia__2020_United_States_House_of_Representatives_elections__12_24_19.html"


def get_states(soup):
	tables = soup.find_all('table', {'class': 'wikitable sortable'})
	cleaned_tables = [
		t for t in tables if (
			"First elected" in t.get_text() and
			"Representative" in t.get_text() and
			"Location" in t.get_text()
		)
	]
	return cleaned_tables


def get_races_from_state(state_html):
	state_races = state_html.find_all('tr')[2:] # remove two header rows
	return state_races


def get_all_races(soup):
	states = get_states(soup)

	races = []
	for state in states:
		races.extend(get_races_from_state(state))
	return races


def extract_candidate_info(candidate_info_string):
	regex = r"(.*) \(([A-z &]*)\)(\[[0-9]*\])?"
	match = re.search(regex, candidate_info_string)
	if match is None:
		return {
			'name': candidate_info_string,
			'extracting_info_success': False		
		}
	if len(match.groups()) >= 2:
		return {
			'name': match.group(1),
			'party': match.group(2),
			'extracting_info_success': True
		}
	else:
		return {
			'name': candidate_info_string,
			'extracting_info_success': False
		}


def race_html_to_object(race_html):
	race_id = race_html.find('th').find('span')['data-sort-value'][:-2] # rm two extraneous chars
	candidates_list = race_html.find_all('td')[-1].find('ul') # the ul in the  last table cell
	candidates = []
	for candidate in candidates_list.find_all('li'):
		candidate_info = extract_candidate_info(candidate.get_text())
		candidates.append(
			{**{'race_id': race_id}, **candidate_info}
		) # merge candidate_info with this dict
	return candidates


def remove_tba_candidates(all_candidates):
	return all_candidates[all_candidates.name != 'TBA']


def get_all_candidates():
	soup = BeautifulSoup(
		open(filename, encoding="utf-8"),
		"html.parser"
	)	

	races = get_all_races(soup)

	all_candidates = []

	for race in races:
		all_candidates.extend(race_html_to_object(race))

	all_candidates = pd.DataFrame.from_records(all_candidates)
	all_candidates = remove_tba_candidates(all_candidates)

	df_has_null_values = all_candidates.isnull().any().any()

	if df_has_null_values:
		print('WARNING: candidates dataframe contains nulls')

	return all_candidates


if __name__ == '__main__':
	candidates = get_all_candidates()
	import pdb
	pdb.set_trace()

