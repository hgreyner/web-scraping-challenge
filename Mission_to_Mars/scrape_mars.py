# Import dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

def init_browser():
    # Excute the chromedriver and start Chrome
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape_info():
    browser = init_browser()

    
    ############## NASA Mars News ##############
    
    # Specify URL
    url = 'http://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # Code to find the Title and Paragraph of first news
    news = soup.find('div', class_='list_text')
    news_title = news.find('div', class_='content_title').text
    news_p = news.find('div', class_='article_teaser_body').text

    
    ############## JPL Mars Space Images - Featured Image ##############
    
    # Specify URL
    url2 = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url2)
    # Click on "Full Image"
    browser.click_link_by_partial_text('FULL IMAGE')

    time.sleep(1)
    
    # Click on "more info"
    browser.click_link_by_partial_text('more info')

    html = browser.html
    soup2 = BeautifulSoup(html, 'html.parser')

    # Find url using parsing by beautiful soup
    featured_image = soup2.find('figure', class_='lede').a['href']

    # Compose url with initial url and image url
    featured_image_url = f'https://www.jpl.nasa.gov/spaceimages{featured_image}'

    
    ############## Mars Weather ##############

    # Specify URL
    url3 = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url3)

    time.sleep(1)

    tweet_html_content = requests.get(url3).text
    soup = BeautifulSoup(tweet_html_content, "lxml")
    tweet_list = soup.find_all('div', class_="js-tweet-text-container")
    #empty list to hold tweet we are going to keep, used to strip useless content from string
    holds_tweet = []
    # Loop that scans every tweet and searches specifically for those that have weather info
    for tweets in tweet_list: 
        tweet_body = tweets.find('p').text
        if 'InSight' and 'sol' in tweet_body:
            holds_tweet.append(tweet_body)
            #break statement to only print the first weather tweet found
            break
        else: 
            #if not weather related skip it and try again
            pass
        
    #cleaned up tweet removes unncessary link to twitter image included in string, :-26 removes the last 26 characters which is the length of the img url
    #after reviewing several links they all appear to work with the value of -26
    mars_weather = ([holds_tweet[0]][0][:-26])


    ############## Mars Facts ##############

    # Specify URL
    url4 = 'https://space-facts.com/mars/'

    # Using Pandas to scrape the table containing facts
    mars_table = pd.read_html(url4)[0]

    # Renaming the table columns
    mars_table.columns=["Description", "Value"]

    # Making the Description the Index
    mars_table.set_index('Description', inplace=True)

    # Exporting dataframe to html table
    mars_facts = mars_table.to_html (classes="table table-striped")

    time.sleep(1)
    ############## Mars Hemispheres ##############

    # Specify URL
    url5 = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url5)

    time.sleep(1)
    
    html = browser.html
    soup5 = BeautifulSoup(html, 'html.parser')

    # Find all information about the items on the page
    all_items = soup5.find_all('div', class_='item')
    # Create empty list for hemisphere urls 
    list_of_urls = []
    # Assign a variable named main_url 
    main_url = 'https://astrogeology.usgs.gov'
    # Loop through the items previously stored
    for i in all_items: 
        # Store title
        title = i.find('h3').get_text()
        # Assign url to a variable that leads to the page where full images are stored
        source_img_url = i.find('a', class_='itemLink product-item')['href']
        # Visit the page where full images are stored 
        browser.visit(main_url + source_img_url)
        # HTML Object
        source_img_html = browser.html
        # Parse HTML with Beautiful Soup
        soup6 = BeautifulSoup(source_img_html, 'html.parser')
        # Pull full image source url information
        img_url = main_url + soup6.find('img', class_='wide-image')['src']
        # Append the retrieved information into a list of dictionaries 
        list_of_urls.append({"title" : title, "img_url" : img_url})
    

    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_weather": mars_weather,
        "mars_facts": mars_facts,
        "hemisphere_image_urls": list_of_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data

    