import pandas as pd
import get_campaign_website
import time


candidates = get_campaign_website.check_arguments()

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Palau': 'PW',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}


def extract_state_and_district(race_id):
	state = race_id[:-2]
	district = race_id[-2:] # this will be a string
	state_abbrev = us_state_abbrev[state]
	return (state_abbrev, district)


def generate_campaign_id(race_id, past_race_id, counter):
	state_abbrev, district = extract_state_and_district(race_id)
	past_state_abbrev, past_district = extract_state_and_district(past_race_id)
	if district == past_district:
		counter = counter + 1
	else: # this is a new district
		counter = 1
	return (
		counter,
		'{}{}{}'.format(state_abbrev, district, f'{counter:02}')
	)


counter = 0

candidates.insert(5, 'campaign_id', '0') # add column

for index, row in candidates.iterrows():

	if index == 0:
		counter_new, campaign_id = generate_campaign_id(
			candidates.iloc[index]['race_id'],
			candidates.iloc[index]['race_id'],
			counter
		)
	else:
		counter_new, campaign_id = generate_campaign_id(
			candidates.iloc[index]['race_id'],
			candidates.iloc[index - 1]['race_id'], # this gonna break on the last one huh
			counter
		)

	counter = counter_new

	candidates.at[index, 'campaign_id'] = campaign_id


candidates.to_csv(
	'all_candidates_info_with_campaign_ids__{}.csv'.format(time.strftime("%Y-%m-%d--%H-%M-%S"))
)
