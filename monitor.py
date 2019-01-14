#!/home/user1/.virtualenvs/apartment-alerter/bin/python
"""
This module will scrape the Equity Residential website periodically, and alert me
when there is an update to the number of 2 BR apartments available.

LOGIC


    Do the comparison like     set(a) == set(b)       (because this doesn't care about order)
    Each is a list of TUPLES

    set(list(a)) == set(list(b))



PROOF - that the comparison logic works


    stuff = [('$3,560', 'Floor 4', 'Available 1/13/2019'), ('$3,610', 'Floor 9', 'Available 1/13/2019'), ('$3,690', 'Floor 12', 'Available 2/23/2019'), ('$3,740', 'Floor 5', 'Available 1/13/2019'), ('$3,960', 'Floor 19', 'Available 2/6/2019')]
    other = [('$3,610', 'Floor 9', 'Available 1/13/2019'), ('$3,560', 'Floor 4', 'Available 1/13/2019'), ('$3,690', 'Floor 12', 'Available 2/23/2019'), ('$3,740', 'Floor 5', 'Available 1/13/2019'), ('$3,960', 'Floor 19', 'Available 2/6/2019')]
    print(stuff == other)
    print(set(stuff) == set(other))


"""


import re
import time

import requests
from bs4 import BeautifulSoup

import constants


EQUITY_URL = 'https://www.equityapartments.com/boston/beacon-hill/the-towers-at-longfellow-apartments'
EMAIL_ADDRESS = constants.EMAIL
MAILGUN_API_KEY = constants.API
MAILGUN_DOMAIN_NAME = constants.DOMAIN


mailgun_endpoint = 'https://api.mailgun.net/v3/' + MAILGUN_DOMAIN_NAME + '/messages'
from_email_string = 'My Equity Alert <' + EMAIL_ADDRESS + '>'


def main():

    # TODO: Add a PUSH / SMS Service

    old = []
    new = []
    count = 0
    while True:
        print('count = ' + str(count))
        old = new
        units_html, quantity = get_and_parse(EQUITY_URL)
        # unit_details = unit_detailer(units_html)
        new = units_list(units_html)
        if set(new) != set(old) and count > 0:
            print(new)
            print('Different!!!!')
            send_email()  # Send Email to Notify me of the change!!
        elif set(new) != set(old) and count == 0:
            print('Different, but this is the first time around')
        elif set(new) == set(old):
            print('Same...')
        time.sleep(600)  # SLEEP 10 minutes
        count += 1


def send_email():
    print('trying to send')
    return requests.post(
        mailgun_endpoint,
        auth=("api", MAILGUN_API_KEY),
        data={"from": from_email_string,
              "to": [EMAIL_ADDRESS],
              "subject": "Equity 2BR Apartments Updated!",
              "text": "Check the site quick!"})


def get_and_parse(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html5lib")
    # print(soup.prettify())
    results = soup.find_all('ea5-unit', value=re.compile("vm\.BedroomTypes\[2\]\.AvailableUnits*"))
    return results, len(results)


def units_list(results):
    apt_list = [None] * len(results)
    for i in range(len(results)):  # iterate through list and preserve index
        specs = results[i].find('div', class_='specs')
        # print(specs)
        # price = specs.find('span', class_='pricing').text
        floor = specs.find('span', string=re.compile("Floor*")).text.strip()
        available = specs.find('p', string=re.compile("Available*")).text.strip()
        apt = (floor, available)  # Create Tuple
        apt_list[i] = apt
    return apt_list


if __name__ == "__main__":
    main()
