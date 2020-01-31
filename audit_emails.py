import imaplib
import email
import json
import pandas as pd
import re
import math
import matplotlib.pyplot as plt
import datetime

import get_campaign_website


candidates = get_campaign_website.check_arguments()


SINCE_DATE = datetime.datetime.strptime('01-01-2020', '%d-%M-%Y')


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
            _date_string_from_date(SINCE_DATE)
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


def check_emails_by_campaign_id():
    """
    checks that emails are going to the right email ID
    intended to confirm that each candidate is registered with their proper email+XXXXX@site.com ID
    """
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
    try:
        conn.close()
    except:
        pass
    conn.logout()


def generate_email_count_histogram():
    conn = connect_to_email()

    count_list = []
    for index, row in candidates.iterrows():
        if row['successful_registration'] == True: # already documented
            count, email_ids = check_campaign_emails_by_id(conn, row['campaign_id'])
            count_list.append(count)

    plt.hist(count_list)
    print(len(count_list), 'campaigns')
    print(sum([1 for count in count_list if count > 0]), 'campaigns with at least one email')
    plt.gca().set(
        title='Frequency Histogram of Candidate Emails',
        ylabel='Frequency',
        xlabel='Number of Emails'
    )
    plt.show()
    import pdb
    pdb.set_trace()


def _date_string_from_date(date):
    return date.strftime('%d-%b-%Y')


def get_email_count_by_date(conn, date):
    start_date = date
    end_date = date + datetime.timedelta(days=1)
    query = conn.search(
        None,
        '(SINCE "{0}" BEFORE "{1}")'.format(
            _date_string_from_date(start_date),
            _date_string_from_date(end_date)
        )
    )
    emails = query[1][0]
    count = len(emails.split())
    return count


def generate_email_histogram_over_time():
    conn = connect_to_email()

    day_count = (datetime.datetime.now() - SINCE_DATE).days # the number of days this has been running
    day_list = [SINCE_DATE + datetime.timedelta(days=i) for i in range(day_count + 1)]

    x = []
    y = []
    for day in day_list:
        x.append(day)
        y.append(get_email_count_by_date(conn, day))
    plt.bar(x, y)
    plt.plot_date(x, y, marker=None)
    plt.gca().set(
        title='Frequency of Candidate Emails',
        ylabel='Count',
        xlabel='Number of Emails per Day'
    )
    plt.show()

if __name__ == '__main__':
    # check_emails_by_campaign_id()
    generate_email_count_histogram()
    # generate_email_histogram_over_time()
