# -*- coding: utf-8 -*-
from selenium import webdriver
import logging
from bs4 import BeautifulSoup
import re
import pandas as pd
log = logging.getLogger('seltest')
log.addHandler(logging.NullHandler())


class WebTest(object):
    """
    A tester object which can be entered and exited:

    tester = WebTest()
    with tester:
       test_base()
    """

    def __enter__(self):
        log.debug('Starting Chrome')

        # start a headless chrome webdriver
        # options are so that it works in Docker
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(30)
        log.debug('Started Chrome')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
        log.debug('Exited Chrome')

    def get_all_links(self):
    
        driver = self.driver

        # LANDING PAGE
        base_url = "https://www.bbc.com"
        driver.get(base_url)
        html = driver.page_source
        # BBC home page
        soup = BeautifulSoup(html,"html.parser")
       
        links_elem = soup.find_all('a',{"class": ["block-link__overlay-link","top-list-item__link"]})
        
       
        # it should return a list with something in it
        links_list = []
        for elem in links_elem:
            link = elem.get("href")
           
            if base_url not in link:
                links_list.append(base_url + link)
            else:
                links_list.append(link)
                
        log.debug('Total links %s', len(links_list))
        return links_list
    
    def extract_info(self,links):
       
        driver = self.driver
        info_list = []
        for link in links:
            res = {}
            res['Link'] = link
            driver.get(link)
            html = driver.page_source
            soup = BeautifulSoup(html,"html.parser")
            if soup.find('h1',{"id":"main-heading"}):
                res["Title"] = soup.find('h1',{"id":"main-heading"}).get_text()
                # regex for description
                regex = re.compile('.*RichTextContainer.*')
                res['Description'] = ' '.join([p.get_text() for p in soup.find_all("div", {"class" : regex})])
                print(link)
                info_list.append(res)
        return info_list 
       
    def export_to_excel(self,data):
        df = pd.DataFrame.from_dict(data)
        print(df.head())
        df.to_excel('bbc_data.xlsx',index=False)

if __name__ == "__main__":
    tester = WebTest()
    with tester:
        tester.test_base()
