from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import os
import time

#TODO Add a feature to export data.
#TODO Intergrate pipeline to seperate people with website and without.

class Crawl:

    def __init__(self):
        self.path = os.path.join("C:\Program Files (x86)\chromedriver", "chromedriver.exe")
        self.driver = webdriver.Chrome(self.path)
        self.listing_arr = []
        self.listing_pages = []
        self.current_page = 0
        self.status = True
        self.run()

    def run(self):
        self.begin_search("Painters", "Longwood, FL")
        self.store_listings()
        self.check_listing_website()

    def wait_for_xpath(self, path):
        return WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, path)))

    def begin_search(self, type, location):
        # Opens up Yelp's Home Page
        self.driver.get("https://www.yelp.com")
        print("[Crawl] Starting scrape")

        # Element for search paramters (Business type) & (Location) (Wait until elment is clickable)
        type_elem = self.wait_for_xpath("/html/body/div[2]/div/div[2]/form/div/div[1]/div/label/div/span[2]/input[2]")
        location_elem = self.wait_for_xpath(
            "/html/body/div[2]/div/div[2]/form/div/div[2]/div/div[1]/div/label/div/span[2]/input[1]")

        # Enter search type and location paramaters
        type_elem.send_keys(type)

        # Clear existing test for location due to auto-filling
        location_elem.clear()
        location_elem.send_keys(location)

        # Start Search
        type_elem.send_keys(Keys.ENTER)

    def store_listings(self):
        # TODO Error being caused by spondred posting appearing and chaning the order

        try:
            listings_elem = WebDriverWait(self.driver, 6).until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/yelp-react-root/div[1]/div[3]/div/div[1]/div[1]/div[2]/div/ul")))
        except TimeoutException:
            listings_elem = WebDriverWait(self.driver, 6).until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/yelp-react-root/div[1]/div[4]/div/div[1]/div[1]/div[2]/div/ul")))

        listing_elems = listings_elem.find_elements_by_class_name("css-166la90")

        for url in listing_elems:
            if str(url.get_attribute("href")).count("search?find") == 0:
                self.listing_arr.append(str(url.get_attribute("href")))
            else:
                self.listing_pages.append(str(url.get_attribute("href")))
        # self.listing_arr[0].click()

    def check_listing_website(self):
        list_count = 0

        if len(self.listing_arr) > 0:
            while self.status is True:
                if list_count == len(self.listing_arr):
                    list_count = 0
                    self.next_page()
                    self.store_listings()

                self.driver.get(self.listing_arr[list_count])

                list_count += 1

                # Check if the listing has a website present.
                try:
                    # WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "css-ac8spe")))
                    website_elem = self.driver.find_elements_by_class_name("css-ac8spe")

                    for website in website_elem:
                        website_elem_text = website.get_attribute("innerText")

                        if str(website_elem_text).count(".") == 1:
                            print(website_elem_text)
                except NoSuchElementException:
                    print("[Crawl] Website Not Found")

    def next_page(self):
        if len(self.listing_pages) == 0:
            return  print("[Error] No pages listed")

        self.driver.get(self.listing_pages[self.current_page])
        self.current_page += 1
        print("Swithcing to page -", self.current_page)