# Python wraper for the DueDil API, with multi-threading
# -*- coding: utf-8 -*-


# Libraries
from Queue import Queue
import threading
import time
import unicodecsv
from random import shuffle

import json

# Local libraries
from scraping import scrape, beautiful_scrape


# Main keys
duedil_api_key="censored"
bing_api_key = "censored"

# File

input_path = 'input/URLlessLiveCompaniesByTurnover_NonForeign.csv'
output_path = 'output/find_websites.csv'
output_path_json = 'output/find_websites.json'

# Scripts

def duedil_company_search(company_name, duedil_api_key):
    # Searches a company by its name
    # Requires scrap

    # Clean company name
    clean_company_name = company_name
    clean_company_name = clean_company_name.lower()
    clean_company_name = clean_company_name.replace(' ', '%20')

    # Do search
    search_url = 'http://duedil.io/v3/companies?filters={"name":"'+clean_company_name+'"}&api_key='+duedil_api_key

    search_response = scrape(search_url)

    if search_response:
        company_url_root = search_response["response"]["data"][0]["company_url"]
        company_url = company_url_root+'?api_key='+duedil_api_key+'&format=json'
        director_url = company_url_root+'/directors'+'?api_key='+duedil_api_key+'&format=json'
    else:
        return False

    # Company profile

    profile_response = scrape(company_url)

    if profile_response and 'response' in profile_response:
        company_profile = profile_response['response']
    else:
        return False

    director_response = scrape(director_url)

    if director_response and 'response' in director_response:
        company_profile['directors'] = director_response['response']['data']
    else:
        return False

    return company_profile


def bing_the_query_field(query_field, bing_api_key, n_results):

    # Forbidden list

    forbidden_list = ["wikipedia", "bloomberg", "companiesintheuk", "duedil", "companycheck", "prnewswire", "google", "companieslist", "linkedin", "endole.co.uk", "tuugo", "companiesireland", "top1000", "directorsintheuk", "companydirectorcheck", "yell", "192.com", "facebook", "solocheck", "reuters.com", "idevon.co.uk", "slideshare"]



    # Bings a query, returns the n first items

    bing_search_url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/Web?Query='+ query_field + '&$format=json'
    #print bing_search_url
    
    bing_response = scrape(bing_search_url, bing_api_key)

    list_of_url = []
    if bing_response:
        if 'd' in bing_response:
            if 'results' in bing_response['d']:
                for result in bing_response['d']['results']:
                    flag = True
                    for element in forbidden_list:
                        if element in result['Url']:
                            flag = False
                    
                    if flag == True:
                        list_of_url.append(result['Url'])


    return list_of_url[:min(len(list_of_url), n_results)]


def check_for_the_info(website_url, dict_of_info_to_check):
    # To scrap a url, grade it with the info asked & return the grade
    grade = 0


    website_content = beautiful_scrape(website_url, None, "text")

    for key, element in dict_of_info_to_check.iteritems():
        #print key
        #print element

        for datapoint in element['data']:

            if datapoint in website_content:
                grade += element['grade']

    print website_url, grade

def turn_into_string(input_list):

    output = ""

    for element in input_list:
        output += element + ','

    return output



def main_action(input_q, result_q, duedil_api_key, bing_api_key):
    # To take an element from the queue and send it to the scraper

    while True:
        
        # Retrieve element once only
        company_name = input_q.get()
        tmp_dict = dict()
        tmp_dict['company_name'] = company_name

        
        ### DueDil ###
        # Search company on DueDil
        duedil_response = duedil_company_search(company_name, duedil_api_key)

        tmp_dict['duedil_profile'] = duedil_response

        if duedil_response:
            if 'id' in tmp_dict['duedil_profile']: tmp_dict['company_id'] = tmp_dict['duedil_profile']['id']
            if 'directors' in tmp_dict['duedil_profile']:
                
                tmp_dict['company_directors_full_name'] = []
                tmp_dict['company_directors_last_name'] = []

                for director in tmp_dict['duedil_profile']['directors']:
                    if "forename" in director and "surname" in director:
                        tmp_dict['company_directors_full_name'].append(director['forename']+' '+director['surname'])
                    if "surname" in director:
                        tmp_dict['company_directors_last_name'].append(director['surname'])

        # Delete the profile
        tmp_dict.pop('duedil_profile', None)

        ### Bing ###
        # Build the query
        clean_company_name = tmp_dict['company_name'].replace(' ', '+')
        clean_company_name = clean_company_name.replace('&', '')
        query_field = "'"+clean_company_name+"'"

        # Do the search
        tmp_dict['bing_urls'] = bing_the_query_field(query_field, bing_api_key, 5)


        ### Check Info ####
        # Info to check & grades
        dict_of_info_to_check = dict()

        if "company_id" in tmp_dict:
            dict_of_info_to_check['company_id'] = dict()
            dict_of_info_to_check['company_id']['data'] = [tmp_dict['company_id']]
            dict_of_info_to_check['company_id']['grade'] = 100

        if "company_name" in tmp_dict:
            dict_of_info_to_check['company_name'] = dict()
            dict_of_info_to_check['company_name']['data'] = [tmp_dict['company_name']]
            dict_of_info_to_check['company_name']['grade'] = 100

        if "company_directors_full_name" in tmp_dict:
            dict_of_info_to_check['company_directors_full_name'] = dict()
            dict_of_info_to_check['company_directors_full_name']['data'] = tmp_dict['company_directors_full_name']
            dict_of_info_to_check['company_directors_full_name']['grade'] = 70

        if "company_directors_last_name" in tmp_dict:
            dict_of_info_to_check['company_directors_last_name'] = dict()
            dict_of_info_to_check['company_directors_last_name']['data'] = tmp_dict['company_directors_last_name']
            dict_of_info_to_check['company_directors_last_name']['grade'] = 60

        
        tmp_dict['confidence'] = []
        
        for website_url in tmp_dict['bing_urls']:
            #tmp_dict["confidence"].append(check_for_the_info(website_url, dict_of_info_to_check)) 
            tmp_dict["confidence"].append(0)



        # Finish the task
        result_q.put(tmp_dict)
        input_q.task_done()


def main():

    # List of companies to find
    companies_file = unicodecsv.reader(open(input_path, "rU"))

    limit = 500
    i = 0
    list_of_companies = []
    
    for row in companies_file:
        list_of_companies.append(row[1])


    shuffle(list_of_companies)

    list_of_companies2 = []

    with open(output_path_json, 'r') as existing_result_file:
        existing_result = existing_result_file.read()

        for element in list_of_companies:
            if element not in existing_result:
                list_of_companies2.append(element)

    list_of_companies2 = list_of_companies2[:min(len(list_of_companies2), limit)]


    # Breaking down into multiple threads
    
    # Init the queues
    num_threads = 5
    url_q = Queue(maxsize=0)
    result_q = Queue(maxsize=0)

    #counter = [0]
    threads = []
    for i in range(num_threads):
        worker = threading.Thread(target=main_action, args=(url_q, result_q, duedil_api_key, bing_api_key))
        worker.setDaemon(True)
        worker.start()
        threads.append(worker)


    for x in list_of_companies2:
        url_q.put(x)


    url_q.join()
    

    output_file = unicodecsv.writer(open(output_path, "a"))
    output_json = open(output_path_json, 'a')
    
    while (not result_q.empty()):
        tmp = result_q.get()
        
        # Build output

        # Company name
        output = [tmp['company_name']]




        # Bing URL & confidence score
        for i in range(5):
            if 'bing_urls' in tmp:
                if i < len(tmp['bing_urls']):
                    output.append(tmp['bing_urls'][i])
                    if 'confidence' in tmp:                    
                        if i < len(tmp['confidence']):
                            output.append(tmp['confidence'][i])
                        else:
                            output.append("")
                    else:
                        output.append("")
                else:
                    output.append("")
                    output.append("")

        if "company_id" in tmp:
            output.append(tmp['company_id'])
        if "company_directors_full_name" in tmp:
            for element in tmp['company_directors_full_name']:
                output.append(element)


        output_file.writerow(output)

        json.dump(tmp, output_json)
        output_json.write("\n")

        
    return True



if __name__ == '__main__':
    print "inside main"
    # main()
