"""
Created by Steven Belcher

TODO:
    - Add email and SMS updates for users
"""
import os
import sys
import argparse
import requests
import webbrowser
from time import sleep
from random import randint
from datetime import datetime
from twilio.rest import Client
from urllib.parse import urljoin
from bs4 import BeautifulSoup as BS

# DEFINING CONSTANTS
HOMEPAGE = "https://www.bestbuy.com"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/83.0.4103.116 Safari/537.36"}

# set to hold found items so they aren't opened repeatedly
TOUCHED = set()
NOTIFIED = set()


parser = argparse.ArgumentParser()


def get_soup(url, headers, timeout=10):
    try:
        res = requests.get(url, headers=headers, timeout=timeout)
        assert res.ok, f"""Got response {res.status_code} from server!"""
        return BS(res.text, 'html.parser')
    except (TimeoutError, Exception) as e:
        # Sometimes we timeout. Not sure why, but all we do is print the error and try again in a few seconds
        print("Error encountered!")
        print(e)
        return None

def get_products(soup):
    return soup.find_all('li', {"class": "sku-item"})

def check_stock(products, in_store):
    global TOUCHED
    global NOTIFIED
    invalid_status = ['SOLD_OUT'] if in_store else ['SOLD_OUT', 'IN_STORE_ONLY']
    for item in products:
        item_id = item.attrs.get("data-sku-id")
        button = item.find('button', {"class": "add-to-cart-button"})
        if button is None:
            button = item.find('a', {"class": "add-to-cart-button"})

        if button and ((status := button.attrs.get('data-button-state')) not in invalid_status):
            e = item.h4.a.attrs.get('href')
            if e and ((item_id, status) not in NOTIFIED):
                # join url, add itemid to the set of visited ids, open a browser tab
                prod_page = urljoin(HOMEPAGE, e)
                TOUCHED |= {(item_id, status)}
                print(f"Opening browser tab for {item.h4.a.string}!")
                webbrowser.open_new_tab(prod_page)

def search_page(url, headers, in_store):
    soup = get_soup(url, headers)
    if soup is None:
        return
    products = get_products(soup)
    check_stock(products, in_store)
    
    # check subsequent pages
    while next_page := soup.find('a', {'class': 'sku-list-page-next'}):
        if next_page.attrs.get('aria-disabled') == 'true':
            break
        if next_url := next_page.attrs.get('href'):
            soup = get_soup(next_url, headers)
            products = get_products(soup)
            check_stock(products, in_store)


def main(url, in_store):
    global TOUCHED
    global NOTIFIED
    global HEADERS
    # main loop
    while True:
        search_page(url, HEADERS, in_store)
        dt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if len(TOUCHED) == 0:
            print(dt, "No inventory found, trying again in a few seconds...")
        else:
            NOTIFIED |= TOUCHED
            print(dt, "Found the following sku(s) in stock:")
            for (itemid, status) in TOUCHED:
                print(f"\t{itemid} - {status}")
            TOUCHED = set()
            print("Checking for new inventory in a few seconds...")
        # wait a bit so the server doesn't kick us out
        sleep(randint(5,10))
        

if __name__ == "__main__":
    parser.add_argument("url", help="BestBuy URL to search", type=str)
    parser.add_argument("--in_store", help="Whether to notify about products listed as In Store Only", default=False, action="store_true")
    args = parser.parse_args()
    main(args.url, args.in_store)



