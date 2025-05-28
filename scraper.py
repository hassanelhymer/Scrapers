from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
ranks = []
champions = []
tiers = []
roles = []
winrates = []
pickrates = []
banrates = []
champions_data = {
    "ranks": ranks,
    "champions": champions,
    "tiers": tiers,
    "roles": roles,
    "winrates": winrates,
    "pickrates": pickrates,
    "banrates": banrates
}

def rank(row):
    rank_tag = row.find("span", {"class": "w-5 text-xs text-gray-400"})
    if rank_tag:
        ranks.append(rank_tag.text.strip())
    else:
        ranks.append(None)
def champion(row):
    title_tag = row.find('strong', {"class": "flex-1 truncate text-xs max-[420px]:sr-only"})
    if title_tag:
        champions.append(title_tag.text.strip())
    else:
        champions.append(None)

def tier(row):
    paths = row.find_all("path")
    for path in paths:
        tier = path.get("d", "")
        if tier == "M10.148 15v-1.554h1.484V6.894h-1.484V5.34h3.416v8.106h1.456V15z":
            tiers.append("Tier 1")
            break
        elif tier == "M9.165 15v-4.298l1.064-1.064h2.478l.308-.308V7.188l-.322-.308h-1.246l-.322.308v1.05H9.193V6.572l1.218-1.232h3.304l1.246 1.246v3.64l-1.064 1.064h-2.478l-.308.308v1.778h3.836V15z":
            tiers.append("Tier 2")
            break
        elif tier == "m10.124 15-1.232-1.232v-1.722h1.946v1.064l.406.406h1.4l.406-.406v-1.792l-.462-.476h-2.52V9.288h2.52l.462-.462V7.258l-.406-.406h-1.4l-.406.406V8.28H8.892V6.572l1.232-1.232h3.64l1.232 1.218v2.478l-1.008 1.008 1.008 1.022v2.716L13.778 15z":
            tiers.append("Tier 3")
            break
        elif tier == "M12.672 15v-2.548H8.64v-1.26L9.998 5.34h1.722l-1.092 5.502h2.044V5.34h1.932v5.502h.714v1.61h-.714V15z":
            tiers.append("Tier 4")
            break
        elif tier == "m10.327 15-1.232-1.232V12.06h1.946v1.022l.392.392h1.218l.406-.406v-2.646l-.308-.322h-1.232l-.616.616H9.095V5.34h5.782v1.61h-3.836v2.31l.686-.686h2.128l1.148 1.148v4.032L13.757 15z":
            tiers.append("Tier 5")
            break
    else:
        tiers.append(None)
def role(row):
    paths = row.find_all("path")
    for path in paths:
        d = path.get("d", "")
        opacity = path.get("opacity", "")
        if d == "m5 21 4-4h8V9l4-4v16z" and opacity == "0.2":
            roles.append("top")
            break
        elif d == "M5.14 2c1.58 1.21 5.58 5.023 6.976 9.953s0 10.047 0 10.047c-2.749-3.164-5.893-5.2-6.18-5.382l-.02-.013C5.45 13.814 3 8.79 3 8.79c3.536.867 4.93 4.279 4.93 4.279C7.558 8.698 5.14 2 5.14 2m14.976 5.907s-1.243 2.471-1.814 4.604c-.235.878-.285 2.2-.29 3.058v.282c.003.347.01.568.01.568s-1.738 2.397-3.38 3.678a27.5 27.5 0 0 0-.208-5.334c.928-2.023 2.846-5.454 5.682-6.856m-2.124-5.331s-2.325 3.052-2.836 6.029c-.11.636-.201 1.194-.284 1.695-.379.584-.73 1.166-1.05 1.733-.033-.125-.06-.25-.095-.375a21 21 0 0 0-1.16-3.08c.053-.146.103-.29.17-.438 0 0 1.814-3.78 5.255-5.564" and opacity == "":
            roles.append("jungle")
            break
        elif d == "m15 3-4 4H7v4l-4 4V3zM9 21l4-4h4v-4l4-4v12z" and opacity == "0.2":
            roles.append("mid")
            break
        elif d == "m19 3-4 4H7v8l-4 4V3z" and opacity == "0.2":
            roles.append("adc")
            break
        elif d == "M12.833 10.833 14.5 17.53v.804L12.833 20h-1.666L9.5 18.333v-.804l1.667-6.696zM7 7.5 9.5 10l-1.667 4.167-2.5-2.5L6.167 10h-2.5L2 7.5zm15 0L20.333 10h-2.5l.834 1.667-2.5 2.5L14.5 10 17 7.5zM13.743 5l.757.833v.834l-1.667 2.5h-1.666L9.5 6.667v-.834L10.257 5z" and opacity == "":
            roles.append("support")
            break
def winrate(row):
    winrate_tag = row.find("td", {"class": "text-xs text-gray-600"})
    if winrate_tag:
        winrates.append(winrate_tag.text.strip())
    else:
        winrates.append(None)
def pickrate(row):
    pickrate_tags = row.find_all("td", class_="text-xs text-gray-600")
    if len(pickrate_tags) > 1:
        pickrate = pickrate_tags[1].text.strip()  
        pickrates.append(pickrate)
    else:
        pickrates.append(None) 

def banrate(row):
    banrate_tag = row.find("td", class_="hidden text-xs text-gray-600 md:table-cell")
    if banrate_tag:
        banrates.append(banrate_tag.text.strip())
    else:
        banrates.append(None)

url = "https://op.gg/lol/champions?position=all"
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    previous_height = 0
    while True:
        # Scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)  # wait for content to load

        # Get current page height after loading more content
        current_height = page.evaluate("document.body.scrollHeight")

        if current_height == previous_height:
            # No new content loaded, break loop
            break
        previous_height = current_height
    main_div = page.locator("div.w-full.overflow-x-auto.border-t.border-t-gray-200")
    main_div.wait_for(state="visible")
    html = page.content()
    soup = BeautifulSoup(html,"lxml")
    rows = [row for row in soup.find_all("tr") if row.find('strong', {"class": "flex-1 truncate text-xs max-[420px]:sr-only"})]
    for row in rows:
    	rank(row)
    	champion(row)
    	role(row)
    	tier(row)
    	pickrate(row)
    	winrate(row)
    	banrate(row)

df = pd.DataFrame(champions_data)
df.to_csv("champion_data.csv", index=False)
browser.close()
