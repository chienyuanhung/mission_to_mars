from splinter import Browser
from bs4 import BeautifulSoup

import re
import pandas as pd

def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape_all():
    # initiate the browser
    browser = init_browser()
    news_title, news_p = mars_news(browser)
    
    marsdata = {
        "news_title" : news_title,
        "news_paragraph" : news_p,
        "feature_image_url" : feature_image(browser),
        "mars_weather" : mars_weather(browser),
        "mars_fact" : mars_fact(),
        "hemisphere_image_urls" : hemisphere_image_urls(browser)
    } 

    print(marsdata)
    return marsdata
    # scraping the data
    # news_title, news_paragraph = mars_news(browser)
    """data = {
         "news_title" : news_title,
        # "news_paragraph" : news_paragraph,
        # "feature_image" : feature_image(browser),
        # "mars_weather" : mars_weather(browser),
        # "mars_fact" : mars_fact(),
        # "hemisphere_image_urls" : hemisphere_image_urls(browser)
    }

    return data"""

# function to find mars news title and paragraph
def mars_news(browser):
    # set the browser
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    browser.is_element_present_by_css('ul.item_list li.slide', wait_time = 3)
    html = browser.html
    # scrapind data with BeautifulSoup
    news_soup = BeautifulSoup(html, 'html.parser')
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        news_title = slide_elem.find('div', class_='content_title').a.text
        news_p = slide_elem.find('div', class_="article_teaser_body").text
    except AttributeError:
        return None, None

    return news_title, news_p

# function to find featured image
def feature_image(browser):
    # set the browser
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    html = browser.html
    # scrapind data with BeautifulSoup, find the link to featured image
    img_soup = BeautifulSoup(html, 'html.parser')
    img_url_rel = img_soup.find('a', class_="fancybox")["data-link"]
    img_url = f"https://www.jpl.nasa.gov{img_url_rel}"
    # scrapind data with BeautifulSoup, find the featured image url
    browser.visit(img_url)
    html = browser.html
    feature_img_soup = BeautifulSoup(html, 'html.parser')
    featured_image_url_rel = feature_img_soup.find('figure', class_= "lede").a['href']
    featured_image_url  = f"https://www.jpl.nasa.gov{featured_image_url_rel}"
    return featured_image_url

# function to find twitter pattern for mars weather data
def findWeather(list):
    for i in list:
        if re.findall(r"^InSight", i.find('p', class_="tweet-text").text):
            return i 

# function for getting mars weather from twitter feed
def mars_weather(browser):
    # set the browser
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    browser.is_element_present_by_css('div.js-tweet-text-container', wait_time = 1)
    html = browser.html
    # scrapind data with BeautifulSoup
    weather_soup = BeautifulSoup(html, 'html.parser')
    weather_elem = weather_soup.find_all('div', class_="js-tweet-text-container")
    weather_feed = findWeather(weather_elem)
    mars_weather = weather_feed.find('p', class_="tweet-text").text.split('pic.twitter')[0]
    mars_weather = mars_weather.replace('\n','')
    return mars_weather

# function for getting mars fact table 
def mars_fact():
    url = 'https://space-facts.com/mars/'
    mars_tables = pd.read_html(url)
    mars_facts = mars_tables[1]
    mars_facts.columns = ['description', 'value']
    mars_facts_html = mars_facts.to_html()
    return mars_facts_html

def hemisphere_image_urls(browser):
    hemisphere_image_urls = []
    # set the browser
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    html = browser.html
    info_soup = BeautifulSoup(html, 'html.parser')
    # get the relative url to accsssing the full image
    url_rel = []
    all_url_rel = info_soup.find_all("div", class_="description")
    for i in all_url_rel:
        j = i.find("a", class_="product-item")
        url_rel.append(j['href'])
    
    # looping throughthe url and get the title and full image url for each image
    for i in url_rel:
        url = f"https://astrogeology.usgs.gov{i}"
        browser.visit(url)
        html = browser.html
        browser.is_element_present_by_css('img.wide-image', wait_time =1)
        link_img_soup = BeautifulSoup(html, 'html.parser')
        img_title = link_img_soup.find('h2', class_ ='title').text
        img_url_rel = link_img_soup.select_one('img.wide-image').get('src')
        img_url = f"https://astrogeology.usgs.gov{img_url_rel}"
        img_dict = {'title': img_title, 'img_url' : img_url}
        hemisphere_image_urls.append(img_dict)
        
    return hemisphere_image_urls