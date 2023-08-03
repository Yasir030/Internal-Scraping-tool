from urllib import parse
import unittest
import sys
import os

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from bots import YahooBot  # noqa


class BaseTest(unittest.TestCase):
    def __init__(self, *args, **keyworgs):
        super().__init__(*args, **keyworgs)


class TestYahooBot(BaseTest):
    def setUp(self) -> None:
        event = {}
        self.LOCAL_MODE = 1
        if self.LOCAL_MODE == 1:
            event["async"] = False
        elif self.LOCAL_MODE == 0:
            event["async"] = True
        self.event = event

        self.searched_keyword = "飯塚幸三"
        # self.searched_keyword = "rock qa"
        self.service = "YAHOO_PC"
        self.parameters = {
            "WISDOM": True,
        }
        self.LOCAL_DEBUG = int(os.environ.get("LOCAL_DEBUG", 0))

        return super().setUp()

    def test_get_page_pc(self):
        yahoo_bot = YahooBot(
            self.searched_keyword,
            service=self.service,
            parameters=self.parameters,
        )
        yahoo_bot.init_driver_local_chrome_debug() if self.LOCAL_DEBUG else yahoo_bot.init_driver_local_chrome()
        yahoo_bot.get_pages_pc()
        yahoo_bot.close()
        yahoo_bot.quit()
