import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
# import detailParser
from lxml import html
import random
import os
import argparse

######################################################################################

def getProxies():
    
    base_proxy = "usa.rotating.proxyrack.net"
    # Generate a list of proxies for the range 10000 to 10099
    stickyProxies = [f"{base_proxy}:{port}" for port in range(9001, 9051)]

    # Randomly select a proxy from the list
    # proxy = "usa.rotating.proxyrack.net:9000"
    proxy = random.choice(stickyProxies)

    proxies = {
        'http': proxy,
        'https': proxy,
    }
    return proxies
# Extract property details

def detailDataGrab(url):
    for i in range(10):
       
        proxies = getProxies()
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": url,
            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        
        # Make the GET request
        # response = requests.get(url, headers=headers, proxies=proxies)
        response = requests.get(url, headers=headers)
        status = response.status_code
        if status!=403:
            return response
        else:
            # print('try again')
            pass

    
def getDetails(url):
    response = detailDataGrab(url)
    details = extract_property_details(response.text)
    # print(details)
    # result = json.dumps(details, indent=4)
    return details

######################################################################################
#########################################################################################
# "referer": "https://www.zillow.com/homes/for_sale/{}_rb/".format(zipcode),


def grabdata(url):
    
    # Define the headers
    for i in range(10):
        time.sleep(0.1)
        proxies = getProxies()
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": "https://www.zillow.com/clayton-county-ga/sold/",
            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        
        # Make the GET request
        # response = requests.get(url, headers=headers, proxies=proxies)
        response = requests.get(url, headers=headers)
        print(response)
        status = response.status_code
        print(f"url: {url}")
        print(f"status from grabdata request: {status}")
        if status!=403:
            return response
        else:
            pass
            # print('try again')




def parse(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the script tag with id "__NEXT_DATA__"
    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
    
    # Extract the text content of the script tag
    if script_tag:
        script_content = script_tag.string
        # Load the content as JSON
        json_data = json.loads(script_content)
    else:
        print("Script tag with id '__NEXT_DATA__' not found.")
        return None, []

    try:
        listings = json_data['props']['pageProps']['searchPageState']['cat1']['searchResults']['listResults']
        print(f"Found {len(listings)} listings on the page.")
    except KeyError as e:
        print(f"Error parsing listings: {e}")
        return None, []
    return json_data, listings


############################################################################################

def getFirst(listing):
      property_data = {
        'street': listing.get('addressStreet', None),
        'city': listing.get('addressCity', None),
        'state': listing.get('addressState', None),
        'zip': listing.get('addressZipcode', None),
        'livingArea': listing.get('area', None),
        #'latitude': listing.get('latLong', {}).get('latitude', None),
        #'longitude': listing.get('latLong', {}).get('longitude', None),
        'status': listing.get('statusType', None),
        'detailUrl': listing.get('detailUrl', None),
     }
      return property_data


def extract_property_details(html_content):
    # Parse the HTML content
    tree = html.fromstring(html_content)

    # Extract the JSON data from the script tag with id "__NEXT_DATA__"
    script_content = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script_content:
        return {"error": "No property data found"}
    
    try:
        # Parse the JSON content
        data = json.loads(script_content[0])

        # Navigate to the nested data structure
        gdp_client_cache = data.get("props", {}).get("pageProps", {}).get("componentProps", {}).get("gdpClientCache", {})
        # if not gdp_client_cache:
        #     return {"error": "gdpClientCache not found"}
        
        # Parse gdpClientCache if it's JSON-serializable
        if isinstance(gdp_client_cache, str):
            gdp_client_cache = json.loads(gdp_client_cache)

        # Extract property data
        data = gdp_client_cache
         
        extracted_details = {}
        key = next(iter(data))
        data = data[key]
         
        # Property Details
        extracted_details['county'] = data['property'].get('county')
        #extracted_details['countyFIPS'] = data['property'].get('countyFIPS')
        #extracted_details['zipPlus4'] = data['property'].get('zipPlus4', '')
        
        # MLS Details
        extracted_details['buildingStyle'] = data['property'].get('homeType', '')
        extracted_details['description'] = data['property'].get('description', '')
        extracted_details['yearBuilt'] = data['property'].get('yearBuilt', 0) 
        extracted_details['lotSizeSquareFeet'] = data['property']['resoFacts'].get('lotSize', '')
        extracted_details['rental'] = data['property'].get('postingIsRental', False)  # Retained for clarity, but can be removed if redundant
        extracted_details['totalBuildingAreaSquareFeet'] = data['property']['resoFacts'].get('buildingArea', 0)

        
        property_data = data.get('property', {})
        reso_facts = property_data.get('resoFacts', {})

       
        # Safely process 'atAGlanceFacts'
        at_a_glance_facts = reso_facts.get('atAGlanceFacts', [])
        if isinstance(at_a_glance_facts, list):
            
            # Year Built
            extracted_details['yearBuilt'] = next((fact['factValue'] for fact in at_a_glance_facts if fact.get('factLabel') == 'Year Built'), None)
            
            # Lot Size
            extracted_details['lotSizeSquareFeet'] = next((fact['factValue'] for fact in at_a_glance_facts if fact.get('factLabel') == 'Lot'), None)
            
            
        return  extracted_details
    except Exception as e:
         # logging.error(f"Unexpected error: {e}")
         print("error2"+ str(e))
         print('******')
         return {"error2": str(e)}
        


def nextpage(json_data):
    searchQuery = "?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A18%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-84.64991163452149%2C%22east%22%3A-84.05287336547852%2C%22south%22%3A33.33989676497524%2C%22north%22%3A33.66139945648228%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A1622%2C%22regionType%22%3A4%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22built%22%3A%7B%22min%22%3A2022%2C%22max%22%3A2024%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22usersSearchTerm%22%3A%22Clayton%20County%20GA%22%7D"
    try:
        nextpage = json_data['props']['pageProps']['searchPageState']['cat1']['searchList']['pagination']['nextUrl']
        next_url = 'https://www.zillow.com'+str( nextpage ) + str(searchQuery)
        return next_url
    except KeyError:
        return None

def main():
    baseurl = "https://www.zillow.com/{}/"
    #url = baseurl.format(zipcode)
    url = "https://www.zillow.com/clayton-county-ga/sold/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A1%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-84.64991163452149%2C%22east%22%3A-84.05287336547852%2C%22south%22%3A33.33989676497524%2C%22north%22%3A33.66139945648228%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A1622%2C%22regionType%22%3A4%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22built%22%3A%7B%22min%22%3A2022%2C%22max%22%3A2024%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22usersSearchTerm%22%3A%22Clayton%20County%20GA%22%7D"
    print(url)

    response = grabdata(url)
    json_data, listings = parse(response)
    results = []
    listingLength = len(listings)
    for listing in listings:
        first_data = getFirst(listing)
        
        url = listing['detailUrl']
        details = getDetails(url)
        combined_data = {**first_data, **details}
        results.append(combined_data)

    for i in range(19):
        if (i > 1):
            url = "https://www.zillow.com/clayton-county-ga/sold/"+str(i)+"_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A"+str(i)+"%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-84.64991163452149%2C%22east%22%3A-84.05287336547852%2C%22south%22%3A33.33989676497524%2C%22north%22%3A33.66139945648228%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A1622%2C%22regionType%22%3A4%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22built%22%3A%7B%22min%22%3A2022%2C%22max%22%3A2024%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22usersSearchTerm%22%3A%22Clayton%20County%20GA%22%7D"
            response2 = grabdata(url)
            json_data2, listings2 = parse(response2)
            for listing in listings2:
                first_data2 = getFirst(listing)
                url = listing['detailUrl']
                details2 = getDetails(url)
                combined_data2 = {**first_data2, **details2}
                results.append(combined_data2)
            listingLength += len(listings2)
            
    print(f"nextpage url: {url}, total listings length: {listingLength}")
    targetYear = ['2022', '2023', '2024']
    found = []
    for prop in results:
        if prop.get("yearBuilt") in targetYear:
            found.append(prop)
    return found
output = main()

#df = pd.DataFrame(output)

print(output)