from playwright.sync_api import sync_playwright
import pandas as pd

website = "https://nextlevelpc.ma/735-pc-gamer?order=product.position.asc&stock=1"

def main():
    print("Starting sync script....")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.route(
            "**/*",
            lambda route: (
                route.abort()
                if route.request.resource_type == "image"
                else route.continue_()
            ),
        )
        page.goto(website)
        page.locator("#js-product-list").wait_for()
        
        scraped_data = []
        
        # 1. SCROLL LOOP FIRST: Scroll down until the back-to-top wrapper appears
        print("Scrolling page layout down...")
        while True:
            page.mouse.wheel(delta_x=0, delta_y=1000)
            page.wait_for_timeout(3500)  # Short wait for DOM updates
            
            if page.locator("#tv-back-top-wrapper").is_visible():
                print("Reached the bottom of the page.")
                break

        # 2. SNAPSHOT ONCE: Get all loaded elements at the same time
        articles = page.locator("#js-product-list div.products > article").all()
        print(f"Extracting data from {len(articles)} loaded products...")

        # 3. SCRAPE LOOP: Loop through them cleanly without duplicates
        for article in articles:
            print("#"*40)
            title = article.locator("h2").first.inner_text().strip()
            price = article.locator("span.price").first.inner_text().strip()
            product_features = [li.inner_text().strip() for li in article.locator("div.product-features > ul > li").all()]
            print(title)
            print(product_features)
            print("#"*40)
            
            scraped_data.append({
                "Product Name": title,
                "Price (MAD)": price,
                "Specs Block": ", ".join(product_features)
            })

        browser.close()
        
        # Convert and save
        df = pd.DataFrame(scraped_data)
        df = df.replace(r"\xa0", " ", regex=True)
        csv_filename = "nextlevel_pc_gamer.csv"
        df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        print(f"\n Success! Saved {len(df)} distinct products to '{csv_filename}'")

if __name__ == "__main__":
    main()
