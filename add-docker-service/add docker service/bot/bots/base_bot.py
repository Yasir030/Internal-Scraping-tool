import requests
import hashlib
from pytz import timezone
from enum import Enum
import datetime

# from bot.bots.recapthca import recapcha
import os
import logging
import uuid
import time
import urllib
import urllib.parse
import re
import traceback

import numpy as np
from bs4.element import Comment
from bs4 import BeautifulSoup
# import aiohttp
# import asyncio
# import decimal

# from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# from http_request_randomizer.requests.proxy.requestProxy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# from joblib import Parallel, delayed
import pandas as pd


CHROMEDRIVER = "/var/task/bin/chromedriver"

class BaseServices(Enum):
    YAHOO_PC = "YAHOO_PC"


class BaseBot:
    TIME_INTERVAL_EACH_SITE = 0.25
    TIME_INTERVAL_BASE = 0.5
    TIME_INTERVAL_EACH_SITE_ADDITIONAL = 0.1
    TIME_INTERVAL_COMPREHEND = 1.0

    XPATH_SITE_URL = ""
    XPATH_SITE_TITLE = ""
    XPATH_SITE_DESCRIPTION = ""
    XPATH_SUGGESTION_KEYWORD_PC = ""
    XPATH_SUGGESTION_INPUT = ""

    def __init__(self, searched_keyword, parameters, *args, **kwargs):
        self.searched_keyword = searched_keyword
        self.parameters = parameters
        self.service = kwargs.get("service", None)
        self.current_dir = os.getcwd()
        self.local_debug = int(os.environ.get("LOCAL_DEBUG", 0))
        self.local_debug = int(os.environ.get("LOCAL_FOLDER", self.local_debug))
        if not self.local_debug:
            self.current_dir = "/tmp"
            os.makedirs("/tmp/out", exist_ok=True)

    def init_driver_local_chrome(self):
        self.mobile = False
        self.FORCE_HEADLESS = True
        self.driver = webdriver.Chrome(
            executable_path="/usr/lib/chromium-browser/chromedriver",
            chrome_options=self._get_option_chrome_headless(),
        )

    def init_driver_local_chrome_debug(self):
        self.mobile = False
        self.FORCE_HEADLESS = False
        self.driver = webdriver.Chrome(
            executable_path="/usr/lib/chromium-browser/chromedriver",
            chrome_options=self._get_option_chrome_headless(),
        )

    def _get_option_chrome_default(self):
        options = Options()
        options.add_argument("--remote-debugging-port=0")
        # options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--single-process")
        options.add_argument("--incognito")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")

        if self.FORCE_HEADLESS or self.headless == 0:
            options.add_argument("--headless")

        return options

    def _get_option_chrome_headless(self):
        options = self._get_option_chrome_default()
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        )

        return options


    def close(self):
        self.driver.close()

    def quit(self):
        self.driver.quit()

    def _delete_local_storage(self):
        self.driver.execute_script("window.localStorage.clear();")

    def _send_keys(self, element, key, count=1):
        try:
            element.send_keys(key)
        except Exception as e:
            raise e

    def _get(self, URL, count=1):
        try:
            self.driver.get(URL)
        except Exception:
            print(traceback.format_exc())

    def _close_after(self):
        pass

    def _disable_scripts(self):
        pass

    def _click(self, element, count=1):
        try:
            element.click()
        except Exception as e:
            raise e

    def _set_window_size(self):
        self.driver.set_window_size(1200, 5000)
        time.sleep(self.TIME_INTERVAL_BASE)

    def _recover_suggestions(self, suggestions):
        pass

    def fetch_main(self, path_html=None, url_suffix=""):
        pass

    def fetch_suggestion_suggestion(self):
        self.driver.delete_all_cookies()
        self._delete_local_storage()
        self.fetch_suggestion(self.path_html_sug, False, "SUGGESTION")

    def fetch_suggestion_sugspace(self):
        self.driver.delete_all_cookies()
        self._delete_local_storage()
        self.fetch_suggestion(self.path_html_sug_space, True, "SUGGESTION_WITH_SPACE")

    def get_pages(self, service):
        pass

    def get_pages_pc(self):
        self.get_pages(self.services.PC)


    def get_sites(self, url=None, service=None, count=1):
        pass

    def _pre_open(self):
        pass

    def _inject_charset(self, html):
        return html

    def _delete_histories(self):
        pass

    def get_suggestions(self, with_space=False, direct=False):
        pass