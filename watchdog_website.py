"""
Watchdog to observe the state of the reservation
"""

from bs4 import BeautifulSoup
from selenium import webdriver
import easygui


class SUZ:
    """
    This class encapsulates methods to login and  get information from the website
    """
    def __init__(self):
        """
        Basic settings needed for browser to work
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        prefs = {"profile.password_manager_enabled": False, "credentials_enable_service": False}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def login(self):
        """
        Login to the account
        """
        self.driver.get('https://web.suz.cvut.cz/Login')
        route1 = '//*[@id="PrihlaseniForm"]/form/div[2]/div/div[1]/div/input'
        route2 = '//*[@id="PrihlaseniForm"]/form/div[2]/div/div[2]/div/input'
        route3 = '//*[@id="PrihlaseniForm"]/form/div[2]/div/div[3]/div/input'
        email = self.driver.find_element_by_xpath(route1)
        email.send_keys("xxxxxxx@gmail.com")
        password = self.driver.find_element_by_xpath(route2)
        password.send_keys("xxxxxx")
        btn_log = self.driver.find_element_by_xpath(route3)
        btn_log.click()

    def switch_page(self):
        """
        Click on the navbar and choose option
        """
        route1 = '//*[@id="bs-example-navbar-collapse-1"]/ul/li[2]/a'
        route2 = '//*[@id="bs-example-navbar-collapse-1"]/ul/li[2]/ul/li[2]/a'
        btn_accom = self.driver.find_element_by_xpath(route1)
        btn_accom.click()
        btn = self.driver.find_element_by_xpath(route2)
        btn.click()

    def parse_page_get_result(self):
        """
        Get the page  parse it with BeautifulSoup and find information
        """
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        for text in soup.find_all("h3", class_="text-centering"):
            if "Vytvoření nové rezervace není v současné době povoleno" \
                    in text.getText():
                easygui.msgbox("NE!", title="SUZ Rezervacia")
                self.driver.close()
                ...
            else:
                easygui.msgbox("Hurra na to!", title="SUZ Rezervacia")
                self.driver.close()


if __name__ == "__main__":
    bot = SUZ()
    bot.login()
    bot.switch_page()
    bot.parse_page_get_result()
