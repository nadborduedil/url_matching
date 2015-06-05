import urllib
import json
import sys

from scraping import scrape

website_blacklist = ["wikipedia", "bloomberg", "companiesintheuk", "duedil",
                     "companycheck", "prnewswire", "google", "companieslist",
                     "linkedin", "endole.co.uk", "tuugo", "companiesireland",
                     "top1000", "directorsintheuk", "companydirectorcheck",
                     "yell", "192.com", "facebook", "solocheck", "reuters.com",
                     "idevon.co.uk", "slideshare",

                     'cylex-uk.co.uk', 'checksure.biz', 'ccdni.com',
                     'bizzy.uk', 'salespider.com', 'locallife.co.uk',
                     'ukplaces.com', 'bizwiki.co.uk', 'yell.com',
                     'findthecompany.co.uk', 'bizdb.co.uk',
                     'bizstats.co.uk', 'privco.com', 'newzealandcorps.com',
                     'brandigg.info', 'businessmagnet.co.uk',
                     'businessnetwordk.co.uk', 'companies-newzealand.com',
                     'scoot.co.uk',
]


def bing_companies(name, bing_api_key, blacklist=website_blacklist):
    """Bings a query, returns the n first items omits urls containing
    blacklisted words"""
    query_field = "'%s'" % urllib.quote(name)
    bing_search_url = \
        'https://api.datamarket.azure.com/Data.ashx/Bing/Search/Web?Query=' + \
        query_field + '&$format=json'

    response = scrape(bing_search_url, bing_api_key)

    list_of_urls = []
    if response and 'd' in response and 'results' in response['d']:
        for result in response['d']['results']:
            if not any(b in result['Url'] for b in blacklist):
                list_of_urls.append(result['Url'])

    return list_of_urls


def main(bing_api_key, company_names_path, output_path):
    with open(company_names_path, "rb") as companies_file, \
            open(output_path, "wb") as output_file:
        for line in companies_file:
            org, name = json.loads(line)
            print "dealing with", name
            urls = bing_companies(name, bing_api_key)
            print "binged"
            output_file.write(json.dumps([org, name, urls]) + "\n")


if __name__ == "__main__":
    _, bing_api_key, company_names_path, output_path = sys.argv
    main(bing_api_key, company_names_path, output_path)