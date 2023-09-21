# WebpageLoader at langchain dynamic page error fix
from embedchain.loaders.web_page import WebPageLoader

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from embedchain.loaders.base_loader import BaseLoader
from embedchain.utils import clean_string
import time
import asyncio

import asyncio
from queue import Queue
import threading

class WebdriverQueue:
    def __init__(self, num):
        self.drivers = Queue()
        self.lock = threading.Lock()

        for _ in range(num):
            service = ChromeService()
            chrome_options = ChromeOptions()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            self.drivers.put(driver)

    def pop_driver(self):
        while True:
            with self.lock:
                if not self.drivers.empty():
                    return self.drivers.get()
            time.sleep(1)
            # Wait or retry if the queue is empty

    def push_driver(self, driver):
        while True:
            with self.lock:
                if not self.drivers.full():
                    self.drivers.put(driver)
                    return
            time.sleep(1)
            # Wait or retry if the queue is full

def webpage_load_loading_fix(self, url):
        """Load data from a web page using Selenium."""
        
        driver = webdrivers.pop_driver()

        content = None
        try:
            driver.get(url)
            # Define a custom Expected Condition to wait for iframes to be loaded
            def all_iframes_loaded(driver):
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    driver.switch_to.frame(iframe)
                    if not driver.execute_script("return document.readyState") == "complete":
                        return False
                    driver.switch_to.default_content()
                return True
            
            # Explicitly wait for the condition to be met (adjust the timeout as needed)
            wait = WebDriverWait(driver, 30)  # Wait up to 30 seconds (adjust as needed)
            
            # Wait for all iframes to be loaded
            wait.until(all_iframes_loaded)

            all_text_content = []
            def extract_text_from_iframe(iframe_element):
                driver.switch_to.frame(iframe_element)
                root_element = driver.find_element(By.TAG_NAME, "html")
                find_iframes_recursively(root_element)
                iframe_page_source = driver.page_source
                iframe_soup = BeautifulSoup(iframe_page_source, "html.parser")
                iframe_text_content = reduce_soup(iframe_soup)
                driver.switch_to.parent_frame()
                driver.execute_script("arguments[0].textContent = arguments[1];", iframe_element, iframe_text_content)

            def find_iframes_recursively(parent_element):
                for child_element in parent_element.find_elements(By.TAG_NAME, "iframe"):
                    find_iframes_recursively(child_element)
                if parent_element.tag_name == "iframe":
                    extract_text_from_iframe(parent_element)
            
            def reduce_soup(orig_soup):
                tags_to_exclude = [
                    "nav",
                    "aside",
                    # "form", # include form to read all iframes
                    "header",
                    "noscript",
                    "svg",
                    "canvas",
                    "footer",
                    "script",
                    "style",
                ]
                for tag in orig_soup(tags_to_exclude):
                    tag.decompose()

                ids_to_exclude = ["sidebar", "main-navigation", "menu-main-menu"]
                for id in ids_to_exclude:
                    tags = orig_soup.find_all(id=id)
                    for tag in tags:
                        tag.decompose()

                classes_to_exclude = [
                    "elementor-location-header",
                    "navbar-header",
                    "nav",
                    "header-sidebar-wrapper",
                    "blog-sidebar-wrapper",
                    "related-posts",
                ]
                for class_name in classes_to_exclude:
                    tags = orig_soup.find_all(class_=class_name)
                    for tag in tags:
                        tag.decompose()

                content = orig_soup.get_text()
                content = clean_string(content)
                return content

                # cleaned_size = len(content)
                # original_size = len(str(orig_soup.get_text()))
                # if original_size != 0:
                #     print(
                #         f"[{url}] Cleaned page size: {cleaned_size} characters, down from {original_size} (shrunk: {original_size-cleaned_size} chars, {round((1-(cleaned_size/original_size)) * 100, 2)}%)"  # noqa:E501
                #     )

            # Start the recursive search from the root element
            root_element = driver.find_element(By.TAG_NAME, "html")
            find_iframes_recursively(root_element)
            
            # iframes = driver.find_elements(By.TAG_NAME, "iframe")
            # for iframe in iframes:
            #     recur(iframe)
            
            # Get the page source
            page_source = driver.page_source
            
            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(page_source, "html.parser")
            content = reduce_soup(soup)
            # Rest of your code for cleaning the page content
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            # Close the WebDriver
            webdrivers.push_driver(driver)

        meta_data = {
            "url": url,
        }

        return [
            {
                "content": content,
                "meta_data": meta_data,
            }
        ]

# webdrivers = WebdriverQueue(5)
# WebPageLoader.load_data = webpage_load_loading_fix