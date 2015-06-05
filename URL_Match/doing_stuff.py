import json
import cgi
from bing_companies import bing_companies
from scraping import beautiful_scrape


bing_api_key = "v/LiByWjAtp4uvoukdPjywY1GPOHxCNAOLPzKKqM1gg="
with open("companies_denorm/microsample", "rb") as inf:
    companies = map(json.loads, inf)


with open("output.txt", "wb") as output:
    for company in companies:
        name = company['name']
        print "binging company: ", name
        urls = bing_companies(name, bing_api_key)
        print "binged urls:", str(urls)[:100]
        urls_websites = []
        for url in urls:
            if len(urls_websites) == 5:
                break
            website = beautiful_scrape(url, timeout=5)
            if website:
                urls_websites.append((url, website))

        # urls_websites = [(url, beautiful_scrape(url)) for url in urls]
        # urls_websites = [(url, web) for url, web in urls_websites if web][:5]
        print "scraped websites"
        for url, web in urls_websites:
            output.write(name + "\t" + url + "\t\n")
        print "written to file"