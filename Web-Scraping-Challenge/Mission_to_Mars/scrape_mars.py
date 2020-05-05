from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import time
import re


def scrape_all():

    # Headless Driver
    browser = Browser("chrome", executable_path="chromedriver.exe", headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Scrape
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    # Get back data
    browser.quit()
    return data


def mars_news(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # Getting Items
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")

    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        news_title = slide_elem.find("div", class_="content_title").get_text()
        news_p = slide_elem.find(
            "div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    # Get Full Image
    full_image_elem = browser.find_by_id("full_image")
    full_image_elem.click()

    # More info
    browser.is_element_present_by_text("more info", wait_time=0.5)
    more_info_elem = browser.find_link_by_partial_text("more info")
    more_info_elem.click()

    # Parsing
    html = browser.html
    img_soup = BeautifulSoup(html, "html.parser")

    # Image URL
    img = img_soup.select_one("figure.lede a img")

    try:
        img_url_rel = img.get("src")

    except AttributeError:
        return None

    #Base URL
    img_url = f"https://www.jpl.nasa.gov{img_url_rel}"

    return img_url


def hemispheres(browser):

    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )

    browser.visit(url)

    # Href
    hemisphere_image_urls = []
    for i in range(4):

        browser.find_by_css("a.product-item h3")[i].click()

        hemi_data = scrape_hemisphere(browser.html)
        
        hemisphere_image_urls.append(hemi_data)

        # Go Back
        browser.back()

    return hemisphere_image_urls


def twitter_weather(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    time.sleep(5)

    html = browser.html
    weather_soup = BeautifulSoup(html, "html.parser")
    
    tweet_attrs = {"class": "tweet", "data-name": "Mars Weather"}
    mars_weather_tweet = weather_soup.find("div", attrs=tweet_attrs)

    try:
        mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()

    except AttributeError:

        pattern = re.compile(r'sol')
        mars_weather = weather_soup.find('span', text=pattern).text

    return mars_weather


def scrape_hemisphere(html_text):
    # Soup
    hemi_soup = BeautifulSoup(html_text, "html.parser")

    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:

        title_elem = None
        sample_elem = None

    hemisphere = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemisphere


def mars_facts():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)

    # Style
    return df.to_html(classes="table table-striped")


if __name__ == "__main__":

    # Log
    print(scrape_all())
