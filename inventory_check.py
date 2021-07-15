""""""
import argparse
import requests
import webbrowser
from time import sleep
from random import randint
from urllib.parse import urljoin
from bs4 import BeautifulSoup as BS

# DEFINING CONSTANTS
HOMEPAGE = "https://www.bestbuy.com"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/83.0.4103.116 Safari/537.36"}

# set to hold found items so they aren't opened repeatedly
TOUCHED = set()

parser = argparse.ArgumentParser()

def get_products(soup):
    return soup.find_all('li', {"class": "sku-item"})

def check_stock(products):
    global TOUCHED
    for i, item in enumerate(products):
        # if the product isn't sold out and we haven't already TOUCHED it, open a window/tab
        button = item.find('button', {"class": "add-to-cart-button"})
        item_id = item.attrs.get("data-sku-id")
        if button and (button.attrs.get('data-button-state') != 'SOLD_OUT'):
            e = item.h4.a.attrs.get('href')
            if e and (item_id not in TOUCHED):
                prod_page = urljoin(HOMEPAGE, e)
                TOUCHED |= {item_id}

                if i == 0:
                    webbrowser.open_new(prod_page)
                else:
                    webbrowser.open_new_tab(prod_page)

def search_page(url, headers):
    res = requests.get(url, headers=headers)
    assert res.ok, f"Got response {res.status_code} from server!"
    soup = BS(res.text, 'html.parser')    
    
    products = get_products(soup)
    check_stock(products)
    
    # check subsequent pages
    pages = soup.find('ol', {'class': 'paging-list'})
    if pages is not None:
        for i in range(1, len(pages)):
            next_url = url.replace('jsp?', f'jsp?cp={i+1}')
            res = requests.get(next_url, headers=headers)
            assert res.ok, f"Got response {res.status_code} from server!"
            soup = BS(res.text, 'html.parser')
            products = get_products(soup)
            check_stock(products)

            
def main(URL):
    global TOUCHED
    global HEADERS
    # main loop
    while True:
        search_page(URL, HEADERS)
        if len(TOUCHED) == 0:
            print("No inventory found, trying again in a few seconds...")
        else:
            print("Found the following item(s) in stock:")
            for item in TOUCHED:
                print(f"\t{item}")

        sleep(randint(5,10))
        

if __name__ == "__main__":
    parser.add_argument("url", help="BestBuy URL to search", type=str)
    args = parser.parse_args()
    main(args.url)



