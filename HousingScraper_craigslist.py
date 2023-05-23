# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 15:48:21 2020

@author: bryce
"""

from bs4 import BeautifulSoup
from requests import get
import pandas as pd
import numpy as np
import time

headers = ({'User-Agent':
            'Mozilla/5.0 (windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

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

for n in range(50):

    # set target url with params
    url = f'https://{region}.craigslist.org/d/apts-housing-for-rent/search/apa?s={n*120}'
    for k,v in params.items():
        if v:
            url = "&".join([url, f"{k}={v}"])
    
    # get webpage
    response = get(url, headers=headers)
    print(response)
    
    # parse html
    html_soup = BeautifulSoup(response.text, 'lxml')
    
    # get housing cards
    house_containers = html_soup.find_all('li', class_ = "result-row")
    
    # extract info from housing cards
    for house in house_containers:
        price = house.find('span', class_ = "result-price")
        if price: 
            if price.text[0] == '$': data['prices'] += [int(price.text[1:])]
            else: data['prices'] += [int(price.text)]
        else: data['prices'] += [None]
        
        location = house.find('span', class_ = "result-hood")
        if location: data['locations'] += [location.text]
        else: data['locations'] += [None]
        
        housing = house.find('span', class_ = "housing")
        if housing:
            housing = housing.text.replace(" ", "").replace("\n", "").split("-")
            if housing[-1]: data['housings'] += [housing]
            else: data['housings'] += [housing[:-1]]
            
        else: data['housings'] += [None]
        
        post_date = house.find('time', class_ = "result-date")
        if post_date: data['post_dates'] += [post_date.text]
        else: data['post_dates'] += [None]
        
        link = house.find('a', class_="result-title hdrlnk").get('href')
        data['links'] += [link]
    
    time.sleep(np.random.random()*2)


# save to file
pd_data = pd.DataFrame.from_dict(data)
pd_data = pd_data.sort_values(by="prices")
pd_data.to_csv("~/Documents/FindHousing/ScrapedCraigslist.csv")
