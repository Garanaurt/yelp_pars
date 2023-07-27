from selenium import webdriver
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import time



yelp_url = 'https://www.yelp.ca/search?find_desc=Day+Spas&find_loc=vancouver%2C+BC'

ChromeDriverManager().install()

#driver get page source
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
        return get_urls(url, count, result)
    else:
        return result


def get_value(soup, id):
    element = soup.find('input', id=id)
    if element:
        value = element.get('value', '-')
    else:
        value = '-'
    return value


#get biz main page and info page  
def get_biz_info_pages(link):
    pages = []
    driver = webdriver.Chrome()
    driver.get(link)
    time.sleep(1)
    biz_info = driver.page_source
    pages.append(biz_info)
    wait = WebDriverWait(driver, 5)
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler')))
        cookie_button.click()
    except Exception:
        pass
    try:
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.css-1p9ibgf a.css-19v1rkv')))
        button.click()
    except Exception:
        try:
            button1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.margin-t1-5__09f24__nx2jL.border-color--default__09f24__NPAKY')))
            button1.click()
            time.sleep(1)  
        except Exception:
            pass  
    biz_info2 = driver.page_source
    pages.append(biz_info2)
    driver.quit()
    return pages



def get_info(links):
    data = []
    for link in links:
        pages = get_biz_info_pages(link)
        if len(pages) == 2:
            soup = BeautifulSoup(pages[0], 'html.parser')
            soup2 = BeautifulSoup(pages[-1], 'html.parser')

            name = get_value(soup=soup2, id='attr_BusinessName')
            if name == '-':
                name = soup.select_one('.headingLight__09f24__N86u1.margin-b1__09f24__vaLrm.border-color--default__09f24__NPAKY h1').get_text()

            site = get_value(soup=soup2, id='attr_BusinessUrl')
            if site == '-':
                try:
                    area = soup.select('section.css-1b3m20f.margin-b2__09f24__CEMjT.border-color--default__09f24__NPAKY p.css-1p9ibgf a')
                    site = area[0].get_text()
                except Exception:
                    site = link



            telephone = get_value(soup=soup2, id='attr_BusinessPhoneNumber')
            if telephone == '-':
                try:
                    sect = soup.select('section.css-1b3m20f.margin-b2__09f24__CEMjT.border-color--default__09f24__NPAKY p.css-1p9ibgf')
                    phone = sect[1].get_text()
                    telephone = phone
                except IndexError:
                    telephone = ''
        
            parsed_url = urlparse(link)
            query_params = parse_qs(parsed_url.query)
            if 'osq' in query_params:
                osq_value = query_params['osq'][0]
                osq_value_text = osq_value.replace('+', ' ')
            else:
                osq_value_text = ' '
            search_category = osq_value_text

            try:
                category_elements = soup.select_one('.display--inline__09f24__c6N_k.margin-r1-5__09f24__ot4bd.border-color--default__09f24__NPAKY')
                categories = ''.join(span.get_text() for span in category_elements.find_all('span'))
                yelp_category = categories
            except Exception:
                yelp_category = ' '

            #search_addres = 


            city = get_value(soup=soup2, id='attr_BusinessCity')
            if city == '-':
                try:
                    addr_area = soup.select('address .raw__09f24__T4Ezm')
                    city = addr_area[-1].get_text().split(',')[0]
                except Exception:
                    city = 'not find'


            try:
                province_element = soup2.find('select', id='attr_BusinessState')
                selected_option = province_element.find('option', selected=True)
                province = selected_option.text.strip()
            except AttributeError:
                province = '-'
            if province == '-':
                try:
                    addr_area = soup.select('address .raw__09f24__T4Ezm')
                    province = addr_area[-1].get_text().split(',')[1].split(' ')[0]
                except Exception:
                    province = 'not find'
            


            subdomain = urlparse(link).netloc.split('.')[-1]
            if subdomain == 'ca':
                country = 'Canada'
            elif subdomain == 'com':
                country = 'USA'
            else:
                country = subdomain

            adress_line1 = get_value(soup=soup2, id='attr_BusinessStreetAddress1')
            adress_line2 = get_value(soup=soup2, id='attr_BusinessStreetAddress2')
            adress = adress_line1 + adress_line2
            if adress == '-' or adress == '--':
                try:
                    adress_area = soup.select('address .raw__09f24__T4Ezm')
                    adress = adress_area[0].get_text()
                except Exception:
                    adress = 'not find'
            try:
                zip = get_value(soup=soup2, id='attr_BusinessZipCode')
            except Exception:
                zip = '-'
            if zip == '-':
                try:
                    addr_area = soup.select('address .raw__09f24__T4Ezm')
                    zip = addr_area[-1].get_text().split(',')[1].split(' ')[1:]
                except Exception:
                    zip = 'not find'


            mail = 'not find'


            data.append([name, site, telephone, search_category, yelp_category, city, province, country, adress, zip, mail])
            
        

        columns = ['Name', 'Site', 'Telephone', 'Search Category', 'Yelp Category', 'City', 'Province', 'Country', 'Address', 'ZIP', 'Mail']
        df = pd.DataFrame(data, columns=columns)


        output_file = 'output.xlsx'
        df.to_excel(output_file, index=False, engine='openpyxl')
        


get_info(get_urls(yelp_url)[:50])

