# -*- coding: utf-8 -*-

import requests
import json

from bs4 import BeautifulSoup


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False
    return True


def scrape(url, auth_credentials=None, format=None):
    # This function is built to extract info from an url, while handling errors
    # It sends back either the content (.text or .json) or None

    try:
        # print url
        headers = {
            'User-agent': 'Mozilla/5.0'
        }

        # Built for Bing API auth system
        if auth_credentials:
            r = requests.get(url, headers=headers,
                             auth=(auth_credentials, auth_credentials),
                             timeout=5)
        else:
            r = requests.get(url, headers=headers, timeout=5)

        # Check if error
        if not r.raise_for_status():
            if format == "text":
                return r.text.encode('utf-8', 'ignore')
            elif is_json(r.text):
                return r.json()
            else:
                return r.text.encode('utf-8', 'ignore')
        else:
            return None
    except requests.exceptions.ConnectionError as e:
        print "Domain does not exist from " + url
    except requests.exceptions.HTTPError as e:
        print "You got an HTTPError from url = " + url + ": ", e.message
    except requests.exceptions.ReadTimeout as e:
        print "You got a timout from url = " + url + ": ", e.message


def beautiful_scrape(url, auth_credentials=None, format=None, timeout=1):
    # Same as scrap, but with beautiful soup to handle the output

    try:
        # print url
        headers = {
            'User-agent': 'Mozilla/5.0'
        }

        # Built for Bing API auth system
        if auth_credentials:
            r = requests.get(url, headers=headers,
                             auth=(auth_credentials, auth_credentials),
                             timeout=timeout)
        else:
            r = requests.get(url, headers=headers, timeout=timeout)

        # Check if error
        if not r.raise_for_status():
            if format == "text":
                raw_text = r.text
                soup = BeautifulSoup(raw_text)
                return soup.get_text()
            elif is_json(r.text):
                return r.json()
            else:
                raw_text = r.text
                soup = BeautifulSoup(raw_text)
                return soup.get_text()

    except requests.exceptions.ConnectionError as e:
        print "Domain does not exist from " + url
    except requests.exceptions.HTTPError as e:
        print "You got an HTTPError from url = " + url + ": ", e.message
    except requests.exceptions.ReadTimeout as e:
        print "You got a timout from url = " + url + ": ", e.message


def raw_soup(url, auth_credentials=None, format=None):
    # Same as scrap, but with beautiful soup to handle the output

    try:
        # print url
        headers = {
            'User-agent': 'Mozilla/5.0'
        }

        # Built for Bing API auth system
        if auth_credentials:
            r = requests.get(url, headers=headers,
                             auth=(auth_credentials, auth_credentials),
                             timeout=5)
        else:
            r = requests.get(url, headers=headers, timeout=5)

        # Check if error
        if not r.raise_for_status():
            if format == "text":
                raw_text = r.text
                soup = BeautifulSoup(raw_text)
                return soup
            elif is_json(r.text):
                return r.json()
            else:
                raw_text = r.text
                soup = BeautifulSoup(raw_text)
                return soup

    except requests.exceptions.ConnectionError as e:
        print "Domain does not exist from " + url
    except requests.exceptions.HTTPError as e:
        print "You got an HTTPError from url = " + url + ": ", e.message