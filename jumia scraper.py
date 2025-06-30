from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import time

url = "https://www.jumia.ma/smartphones-android/"
close_button_selector = "button.cls[aria-label='newsletter_popup_close-cta']"
base_url = "https://www.jumia.ma"

# Lists to store data
titles, prices, stocks, ratings, product_links = [], [], [], [], []

def rating_stars(text):
    try:
        return round(float(text.split(" ")[0]), 1)
    except:
        return None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    try:
        page.locator(close_button_selector).click()  # Close popup
    except:
        pass

    # Collect product links
    products = page.locator("article.prd._fb.col.c-prd a.core")
    for i in range(products.count()):
        href = products.nth(i).get_attribute("href")
        product_links.append(urljoin(base_url, href))
    page.close()

    # Scrape each product page
    for link in product_links:
        page2 = browser.new_page()
        page2.goto(link)
        try:
            page2.locator(close_button_selector).click()
        except:
            pass
        soup = BeautifulSoup(page2.content(), "lxml")

        title = soup.find("h1")
        titles.append(title.text.strip() if title else "Without a name")

        price = soup.find("span", class_="-b -ubpt -tal -fs24 -prxs")
        prices.append(price.text.strip() if price else "Without a price")

        rating = soup.find("div", class_="stars _m _al")
        ratings.append(rating_stars(rating.text.strip()) if rating else None)

        stock = soup.find("p", class_="-df -i-ctr -fs12 -pbs -rd5") or soup.find("p", class_="-df -i-ctr -fs12 -pbs -yl7")
        stocks.append(stock.text.strip() if stock else "Out of stock")

        page2.close()
        time.sleep(2)

df = pd.DataFrame({
    "Title": titles,
    "Price": prices,
    "Stock": stocks,
    "Rating": ratings,
    "Links": product_links
})

df.to_csv('Products infos.csv', index=False)
