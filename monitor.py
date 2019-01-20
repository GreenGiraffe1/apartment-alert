"""
This module will scrapes an apartment website periodically, and alerts
when there is an update to the number of 2 BR apartments available.

The comparision is made between two sets of tuples (each containing info about a single apartment unit).
Every 10 minutes the "new" set will be updated, and compared with it's former value to determine
if there has been any change to the unit listings.


    LOGIC

    Do the comparison like     set(a) == set(b)       (because this doesn't care about order)
    Each is a list of TUPLES

    set(list(a)) == set(list(b))

"""


import re
import time

import requests
from bs4 import BeautifulSoup
from twilio.rest import Client


from constants import TWILIO_SID, TWILIO_AUTH_TOKEN, FROM_PHONE, TO_PHONE, MAILGUN_DOMAIN_NAME, MAILGUN_API_KEY, EMAIL_ADDRESS, SITE_URL


MESSAGE = '2BR Apartments List Updated!'


mailgun_endpoint = 'https://api.mailgun.net/v3/' + MAILGUN_DOMAIN_NAME + '/messages'
from_email_string = 'My Apartment Alert <' + EMAIL_ADDRESS + '>'


def main():

    old = []
    new = []
    count = 0
    while True:
        print('count = ' + str(count))
        old = new
        units_html, quantity = get_and_parse(SITE_URL)
        # unit_details = unit_detailer(units_html)
        new = units_list(units_html)
        if set(new) != set(old) and count > 0:
            print(new)
            print('Different!!!!')
            send_email()  # Send Email to Notify me of the change!!
            send_sms()
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
              "subject": MESSAGE,
              "text": "Check the site quick!"})


def send_sms():

    # Your Account Sid and Auth Token from twilio.com/console
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_=FROM_PHONE,
        body=MESSAGE,
        to=TO_PHONE
    )
    print("SMS sent!")
    print(message.sid)


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
