# bb-scan
Inventory checker for BestBuy.

## To use

1. Install python 3.8+ from [here](https://www.python.org/downloads/release/python-380/) - make sure to select "Add to Path" checkbox in the installer
2. Copy or clone the repository with git or by clicking code-> Download ZIP
3. If you downloaded the ZIP, unzip to a location you'll remember
4. Open a terminal/cmd and navigate to the folder containing inventory_check.py
5. run `python -m pip install -r requirements.txt`
6. run `python inventory_check.py "[URL]"`

It is important that the provided URL contains all search criteria before running the process! This means that you should use the BestBuy website's filter features to select the categories, products, pricepoint, etc you want BEFORE copying the URL. The script is not designed to check individual item pages, just the lists of search results.

It is also necessary for the provided URL to be in quotes.

The script will continually query the provided url and look for items that are listed as in stock. For each item found, a browser tab is automatically opened to the item page(s). Once a broser tab for an item is opened, the listing is added to a log, and the page for that item will not be reopened until the script is restarted. 
