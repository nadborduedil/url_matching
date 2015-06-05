# Python wraper for the DueDil API, with multi-threading
# -*- coding: utf-8 -*-


# Libraries
from Queue import Queue
import threading
import time
import unicodecsv

# Local libraries
from scrap import scrap


# Main keys
duedil_api_key="7rwksygwzegunxrm5nuke5wz"
bing_api_key = "v/LiByWjAtp4uvoukdPjywY1GPOHxCNAOLPzKKqM1gg="

def duedil_company_search(company_name, duedil_api_key):
    # Searches a company by its name
    # Requires scrap

    # Clean company name
    clean_company_name = company_name
    clean_company_name = clean_company_name.lower()
    clean_company_name = clean_company_name.replace(' ', '%20')

    # Do search
    search_url = 'http://duedil.io/v3/companies?filters={"name":"'+clean_company_name+'"}&api_key='+duedil_api_key

    search_response = scrap(search_url)

    if search_response:
        company_url_root = search_response["response"]["data"][0]["company_url"]
        company_url = company_url_root+'?api_key='+duedil_api_key+'&format=json'
        director_url = company_url_root+'/directors'+'?api_key='+duedil_api_key+'&format=json'
    else:
        return False

    # Company profile

    profile_response = scrap(company_url)

    if profile_response and 'response' in profile_response:
        company_profile = profile_response['response']
    else:
        return False

    #director_response = scrap(director_url)

    #if director_response and 'response' in director_response:
    #    company_profile['directors'] = director_response['response']['data']
    #else:
    #    return False

    return company_profile


def bing_the_query_field(query_field, bing_api_key, n_results):
    # Bings a query, returns the n first items

    bing_search_url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/Web?Query='+ query_field + '&$format=json'
    #print bing_search_url
    
    bing_response = scrap(bing_search_url, bing_api_key)

    list_of_url = []
    if bing_response:
        if 'd' in bing_response:
            if 'results' in bing_response['d']:
                for result in bing_response['d']['results']:
                    list_of_url.append(result['Url'])


    return list_of_url[:min(len(list_of_url), n_results)]



def main_action(input_q, result_q, duedil_api_key, bing_api_key):
    # To take an element from the queue and send it to the scraper

    while True:
        
        # Retrieve element once only
        company_name = input_q.get()
        tmp_dict = dict()
        tmp_dict['company_name'] = company_name

        
        ### DueDil ###
        # Search company on DueDil
        #duedil_response = duedil_company_search(company_name, duedil_api_key)

        #tmp_dict['duedil_profile'] = duedil_response

        #if duedil_response:
            #if 'id' in tmp_dict['duedil_profile']: tmp_dict['company_id'] = tmp_dict['duedil_profile']['id']
            #if 'directors' in tmp_dict['duedil_profile']:
                
                #tmp_dict['company_directors_full_name'] = []
                #tmp_dict['company_directors_last_name'] = []

                #for director in tmp_dict['duedil_profile']['directors']:
                    #tmp_dict['company_directors_full_name'].append(director['forename']+' '+director['surname'])
                    #tmp_dict['company_directors_last_name'].append(director['surname'])

        # Delete the profile
        #tmp_dict.pop('duedil_profile', None)

        ### Bing ###
        # Build the query
        clean_company_name = tmp_dict['company_name'].replace(' ', '+')
        clean_company_name = clean_company_name.replace('&', '')

        query_field = "'"+clean_company_name+"+investors+relations'"

        tmp_dict['bing_urls'] = bing_the_query_field(query_field, bing_api_key, 5)


        # Finish the task
        result_q.put(tmp_dict)
        input_q.task_done()


def main():

    # List of companies to find
    UK_PLCs = unicodecsv.reader(open("UK-PLCs.csv", "rU"))

    limit = 200
    i = 0
    list_of_companies = []
    
    for row in UK_PLCs:
        if i < limit:
            i += 1
            list_of_companies.append(row[1])

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


    for x in list_of_companies:
        url_q.put(x)


    url_q.join()
    

    output_file = unicodecsv.writer(open('results_investors.csv', "a"))

    
    while (not result_q.empty()):
        tmp = result_q.get()
        
        # Build output

        output = [tmp['company_name']]
        for i in range(5):
            if 'bing_urls' in tmp:
                
                if i < len(tmp['bing_urls']):
                    output.append(tmp['bing_urls'][i])


        output_file.writerow(output)
        
    #return result_list



if __name__ == '__main__':

    main()
