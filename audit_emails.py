import imaplib
import email
import json
import pandas as pd

import get_campaign_website


candidates = get_campaign_website.check_arguments()

SINCE_DATE_STRING = '01-Jan-2020'

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


def print_email_detail_by_email_id(connection, email_id):
    typ, msg_data = connection.fetch(email_id, '(RFC822)')
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            print(msg['subject'], '    ', msg['from'])
            # payload = msg.get_payload()
            # body = extract_body(payload)
            # print(body)


conn = connect_to_email()

for index, row in candidates.iterrows():
    if row['successful_registration'] == True: # already documented
        count, email_ids = check_campaign_emails_by_id(conn, row['campaign_id'])
        print(row['name'], '   ', count, 'emails found')
    # todo add checks to confirm the proper campaign id
    # todo add check based on sender website (does it match the campaign website?)
    # todo add check based on candidate name
        # (is it in the body of each email?, inc. first/last names separately)

try:
    conn.close()
except:
    pass
conn.logout()
