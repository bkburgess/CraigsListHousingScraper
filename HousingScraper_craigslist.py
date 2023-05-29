# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 15:48:21 2020

@author: bryce
"""

from bs4 import BeautifulSoup
from requests import get
import pandas as pd
import numpy as np
from time import sleep
from datetime import date
import logging

from pathlib import Path, is_file
SAVE_PATH = Path(__file__).parent / "data"


def setup():
    headers = ({'User-Agent': 'Mozilla/5.0 (windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

    # logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"data path is {SAVE_PATH}")

    # apply filters
    region = 'sfbay'
    params = {
        'search_distance': '',
        'postal': '',
        'min_price': '',
        'max_price': '',
        'min_bedrooms': '',
        'max_bedrooms': '',
        'availabilityMode': '', # when it's available 0: all dates, 1: within 30 days, 2: beyond 30 days
        'sale_date': 'all+dates' # open house date formatted as 2020-07-15 yyyy-mm-dd
    }

    data = {
        'prices' : [],
        'locations' : [],
        'housings' : [],
        'post_dates' : [],
        'links' : []
    }
    return headers, region, params, data

def extract(headers, region, params, data):
    for n in range(50):

        # set target url with params
        url = f'https://{region}.craigslist.org/d/apts-housing-for-rent/search/apa?s={n*120}'
        for key, value in params.items():
            if value:
                url = "&".join([url, f"{key}={value}"])
        
        # get webpage
        response = get(url, headers=headers)
        print(response)
        
        # parse html
        html_soup = BeautifulSoup(response.text, 'lxml')
        
        # get housing cards
        house_containers = html_soup.find_all('li', class_ = "result-row")
        
        # extract info from housing cards
        for house in house_containers:

            # Get the prices of housing options
            price = house.find('span', class_ = "result-price")
            if price: 
                if price.text[0] == '$': data['prices'] += [int(price.text[1:])]
                else: data['prices'] += [int(price.text)]
            else: data['prices'] += [None]
            
            # Get the location of housing options
            location = house.find('span', class_ = "result-hood")
            if location: data['locations'] += [location.text]
            else: data['locations'] += [None]
            
            housing = house.find('span', class_ = "housing")
            if housing:
                housing = housing.text.replace(" ", "").replace("\n", "").split("-")
                if housing[-1]: data['housings'] += [housing]
                else: data['housings'] += [housing[:-1]]
                
            else: data['housings'] += [None]
            
            # Get the date the listing was posted
            post_date = house.find('time', class_ = "result-date")
            if post_date: data['post_dates'] += [post_date.text]
            else: data['post_dates'] += [None]
            
            # Get the url to the listing
            link = house.find('a', class_="result-title hdrlnk").get('href')
            data['links'] += [link]
        
        sleep(np.random.random()*2)
    return data


def save_to_csv(data, region):
    # save to file
    pd_data = pd.DataFrame.from_dict(data)
    pd_data = pd_data.sort_values(by="prices")
    # set file name to include region, search date, and count for multiple searches in same day
    file_name = configure_file_name(region)
    pd_data.to_csv(str(SAVE_PATH / file_name))

def configure_file_name(region):
    file_name = f"{region}_housing_{date.today().isoformat()}"
    i = 1
    while Path(SAVE_PATH / file_name / f"_search_{i}.csv").is_file(): i += 1
    return file_name + f"_search{i}.csv"


if __name__ == '__main__':
    headers, region, params, data = setup()
    data = extract(headers, region, params, data)
    save_to_csv(data, region)