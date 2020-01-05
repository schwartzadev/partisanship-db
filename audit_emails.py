import imaplib
import email
import json
import pandas as pd
import re
import math

import get_campaign_website


candidates = get_campaign_website.check_arguments()

SINCE_DATE_STRING = '01-Dec-2019'
# SINCE_DATE_STRING = '01-Jan-2020'

with open('user_info.json') as json_file:
    data = json.load(json_file)
    GMAIL_USERNAME = data['username'] + '@gmail.com'
    GMAIL_PASSWORD = data['password']


def extract_body(payload):
    if isinstance(payload,str):
        return payload
    else:
        return '\n'.join([extract_body(part.get_payload()) for part in payload])


def connect_to_email():
    conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    conn.login(GMAIL_USERNAME, GMAIL_PASSWORD)
    conn.select('"[Gmail]/All Mail"')
    return conn


def check_campaign_emails_by_id(connection, campaign_id):
    typ, data = connection.search(
        None,
        'TO "partisanshipdatabase+{0}@gmail.com" SINCE "{1}"'.format(
            campaign_id,
            SINCE_DATE_STRING
        )
    )

    return len(data[0].split()), data[0].split()


def get_email_by_email_id(connection, email_id):
    typ, message_data = connection.fetch(email_id, '(RFC822)')
    message = None
    for response_part in message_data:
        if isinstance(response_part, tuple):
            message = email.message_from_bytes(response_part[1])
            # print(message['subject'], '    ', message['from'])
            # payload = message.get_payload()
            # body = extract_body(payload)
            # print(body)
    return {
        'typ': typ,
        'message_data': message_data,
        'message': message
    }


domain_regex = r"(http[s]?://)?([w]{3}[\.])?([A-z-_0-9]*\.[A-z]{2,4})"


def clean_website_url(web_url):
    if isinstance(web_url, float) and math.isnan(web_url):
        return None
    match = re.match(domain_regex, web_url)
    try:
        return match.groups()[2]
    except IndexError as e:
        print('no domain found in', web_url)
        return None


def check_if_string_from_sender(check_string, email_message):
    return check_string.lower() in email_message['from'].lower()


conn = connect_to_email()

for index, row in candidates.iterrows():
    if row['successful_registration'] == True: # already documented
        count, email_ids = check_campaign_emails_by_id(conn, row['campaign_id'])
        for eid in email_ids:
            # print(row['name'], '   ', count, 'emails found')
            email_content = get_email_by_email_id(conn, eid)

            web_domain = clean_website_url(row['website'])
            is_from_domain = check_if_string_from_sender(
                web_domain,
                email_content['message']
            )

            if not is_from_domain: # does the sender match the campaign website?
                print(
                    'WARNING: no domain match:',
                    row['name'],
                    row['campaign_id'],
                    email_content['message']['from'],
                    '   domain:',
                    web_domain,
                    'name check:',
                    [check_if_string_from_sender(n, email_content['message']) for n in row['name'].split()]
                )

    # todo add checks to confirm the proper campaign id

try:
    conn.close()
except:
    pass
conn.logout()
