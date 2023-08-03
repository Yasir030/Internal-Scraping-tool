import re
import os
import time
import urllib.parse
import urllib

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import psycopg2


from . import BaseBot, BaseServices


class Services:
    PC = BaseServices.YAHOO_PC.value


class YahooBot(BaseBot):
    ROOT_URL = "https://search.yahoo.co.jp/search?p="
    XPATH_SUGGESTION_INPUT = '//*[@name="p"]'

    XPATH_YAHOO_PAGE_URL_KEYWOARD_PC = '//*[@id="contents__wrap"]//div[@class="sw-Card__title"]/a'
    XPATH_YAHOO_WISDOM_ROOT_KEYWORD_PC = '//*[@id="sr"]//li[@class="ListSearchResults_listSearchResults__listItem__F0427"]'

    #These xpaths will be concatenated after the 'XPATH_YAHOO_WISDOM_ROOT_KEYWORD_PC' xpath
    XPATH_WISDOM_TITLE_AND_LINK_KEYWORD_PC = '//a'
    XPATH_WISDOM_ANSWER_KEYWORD_PC = '//p[@class="ListSearchResults_listSearchResults__summary__3VWzs"]'
    XPATH_WISDOM_DATE_KEYWORD_PC = '//p[2]'


    def __init__(
        self, searched_keyword, parameters, *args, **kwargs
    ):
        super(YahooBot, self).__init__(
            searched_keyword, parameters, *args, **kwargs
        )

        self.services = Services

    def fetch_yahoo_page_wisdom(self):

        URL = f"{self.ROOT_URL}+{self.entry_keyword}&start={0}"
        self._get(URL)
        time.sleep(self.TIME_INTERVAL_BASE)
        df_yahoo_wisdom = self.get_yahoo_page_wisdom()
        df_yahoo_wisdom["rank"] = int(1)

        #Create csv for Wisdom Questions and Answer's URL
        df_yahoo_wisdom.to_csv(
            f"out/{self.service}/{self.searched_keyword}/yahoo_wisdom.csv", index=False
        )

        # call insert_to_postgresdb_yahoo_page_wisdom method to insert data into PostgreSQL
        self.insert_to_postgresdb_yahoo_page_wisdom(df_yahoo_wisdom)

    def get_yahoo_page_wisdom(self):
        type_ = "WISDOM"
        if not os.path.exists(f"out/{self.service}/{self.searched_keyword}"):
            os.makedirs(f"out/{self.service}/{self.searched_keyword}")


        time.sleep(self.TIME_INTERVAL_BASE)
        search = self.driver.find_element(By.XPATH,self.XPATH_SUGGESTION_INPUT)
        self._click(search)
        time.sleep(self.TIME_INTERVAL_BASE)

        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.set_window_size(1920, scroll_height)
        self.driver.save_screenshot(
            f"out/{self.service}/{self.searched_keyword}/PAGE.png"
        )

        #common part of wisdom url
        wisdom_common_part_link = "https://chiebukuro.yahoo"

        #Page URLs
        yahoo_page_url = self.driver.find_elements(By.XPATH, self.XPATH_YAHOO_PAGE_URL_KEYWOARD_PC)

        wisdom_found = False
        index = 0
        while index < len(yahoo_page_url) and not wisdom_found:
            wisdom_url = yahoo_page_url[index]
            click_url = wisdom_url.get_attribute('href')

            #check wisdom QA exist or not
            if wisdom_common_part_link in click_url:
                self._click(wisdom_url)
                time.sleep(1)
                # Take screenshot for wisdom page
                scroll_height = self.driver.execute_script("return document.body.scrollHeight")
                self.driver.set_window_size(1920, scroll_height)
                self.driver.save_screenshot(f"out/{self.service}/{self.searched_keyword}/{type_}.png")  
                wisdom_found = True
            index+=1

        #Store wisdom data here
        titles = []
        co_links = []
        answer_texts = []
        dates = []

        #find root elements of wisdom
        root_wisdom_element = self.driver.find_elements(By.XPATH, self.XPATH_YAHOO_WISDOM_ROOT_KEYWORD_PC)
        for element in root_wisdom_element:
            #fetch particular titles of wisdom
            title_link = element.find_elements(By.XPATH, f".{self.XPATH_WISDOM_TITLE_AND_LINK_KEYWORD_PC}")
            titles.append(title_link[0].text if title_link else "Not found")

            #fetch particular co-rresponding link of wisdom
            co_links.append(title_link[0].get_attribute('href') if title_link else "Not found")

            #fetch particular Answer of wisdom
            answer = element.find_elements(By.XPATH, f".{self.XPATH_WISDOM_ANSWER_KEYWORD_PC}")
            answer_texts.append(answer[0].text if answer else "Not found")

            #fetch particular date of wisdom
            date = element.find_elements(By.XPATH, f".{self.XPATH_WISDOM_DATE_KEYWORD_PC}")
            dates.append(date[0].text.split("：")[1].split()[0] if date else "Not found")
  
        #Create data-frame for the lists
        df_yahoo_wisdom_result = pd.DataFrame({'Title': titles, 'Co-Link': co_links, 'Answer': answer_texts, 'Date': dates})

        df_yahoo_wisdom_result["type"] = type_

        return df_yahoo_wisdom_result
    
    def insert_to_postgresdb_yahoo_page_wisdom(self,df_yahoo_wisdom_result):
        #connection with postgresdb
        conn = psycopg2.connect(
                    database="test",
                    port="5432",
                    user="testuser",
                    password="1234",
                    host="172.18.0.3"
                    )
        cursor = conn.cursor()

        for _, row in df_yahoo_wisdom_result.iterrows():
            title = row['Title']
            co_link = row['Co-Link']
            answer = row['Answer']
            date = row['Date']

            # insert data to the yahoobot table
            insert_query = f"INSERT INTO yahoobot (title, co_link, answer, date) VALUES ('{title}', '{co_link}', '{answer}', '{date}')"
            cursor.execute(insert_query)
        
        conn.commit()
        cursor.close()
        conn.close()

    def get_pages_preprocess(self):
        entry_keyword = self.searched_keyword
        _entry_keyword = self.searched_keyword.replace("/", "-")
        self.entry_keyword = entry_keyword = urllib.parse.quote(entry_keyword)
        self.URL = self.ROOT_URL.format(self.entry_keyword)

    def get_pages(self, service):
        self.service = service
        self.get_pages_preprocess()

        print("サイトを取得しました。")
        if "WISDOM" in self.parameters:
            if self.parameters["WISDOM"]:
                print("サジェストを取得しています。")
                self.fetch_yahoo_page_wisdom()
                print("サジェストを取得しました。")
