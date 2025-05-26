from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import pandas as pd
import time
url = "https://www.jumia.ma/catalog/?q=carte+graphique"
close_button_selector = "button.cls[aria-label='newsletter_popup_close-cta']"
titles = []
prices = []
stocks = []
ratings = []
products_infos = {
                "Title":titles,
                "Price":prices,
                "Stock":stocks,
                "Rating":ratings
}

def rating_stars(rating_cvt):
    try:
        value = float(rating_cvt.split(" ")[0])
        return round(value,1)
    except:
        return None
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    if url:
        print("Url is valid ,starting a browser tab....")
        page = browser.new_page()
        page.goto(url)
    print("closing newlatter popup....")
    try:
        page.locator(close_button_selector).click()
    except:
        pass
    print("getting products links.... ")
    product_locator = page.locator("article.prd._fb.col.c-prd a.core")
    count = product_locator.count()
    product_links = []
    for i in range(count):
        href = product_locator.nth(i).get_attribute("href")
        product_url = urljoin(url,href)
        product_links.append(product_url)
    page.close()
    for product_link in product_links:
        print(f"Scraping Product number{product_link[i]} starting a new tab....")
        page2 = browser.new_page()
        print("closing page 1....")
        print("Surfing to Product url....")
        page2.goto(product_link)
        try:
            page2.locator(close_button_selector).click()
        except:
            pass
        html = page2.content()
        soup = BeautifulSoup(html, "lxml")
        title_tag = soup.find("h1")
        if title_tag :
            title = title_tag.text.strip()
            titles.append(title)
        else :
            title = "Without a name"
            titles.append(title)
        price_class = soup.find("span",{"class":"-b -ubpt -tal -fs24 -prxs"})
        if price_class:
            price = price_class.text.strip()
            prices.append(price)
        else:
            price = "Without a price"
            prices.append(price)
        rating_class = soup.find("div",{"class":"stars _m _al"})
        if rating_class:
            rating_cvt = rating_class.text.strip()
            rating = rating_stars(rating_cvt)
            ratings.append(rating)
        stock_class = soup.find("p",{"class":"-df -i-ctr -fs12 -pbs -rd5"})
        if not stock_class:
            stock_class = soup.find("p",{"class":"-df -i-ctr -fs12 -pbs -yl7"})
        if stock_class:
            stock = stock_class.text.strip()
        else:
            stock = "Out of stock" 
        stocks.append(stock)

        page2.close()
        time.sleep(2)
            
df = pd.DataFrame(products_infos)
df.to_csv('Products infos.csv',index = False)
