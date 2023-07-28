from selenium import webdriver
from bs4 import BeautifulSoup
import time


def get_page(link):
    driver = webdriver.Chrome()
    driver.get(link)
    time.sleep(1)
    products = driver.page_source
    driver.quit()
    return products

#get url list for pars
def get_urls(url, count=0, result=[]):
    page_content = get_page(url + '&start=' + str(count))
    soup = BeautifulSoup(page_content, 'html.parser')
    products = soup.select('#main-content ul li')
    for prod in products:
        a_tag = prod.find('a', class_='css-1hqkluu')
        if a_tag:
            lin = 'https://www.yelp.ca' + a_tag['href']
            result.append(lin)
    next_btn = soup.select_one('.next-link.navigation-button__09f24__m9qRz.css-ahgoya')
    if next_btn:
        count += 10
        print(result)
        return get_urls(url, count, result[2:11])
    else:
        return result