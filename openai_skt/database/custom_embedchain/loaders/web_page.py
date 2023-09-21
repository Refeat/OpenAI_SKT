import logging
import urllib
import hashlib

import asyncio
import aiohttp
from aiohttp import ClientTimeout
import requests
from bs4 import BeautifulSoup

from embedchain.helper_classes.json_serializable import register_deserializable
# from embedchain.loaders.base_loader import BaseLoader
from embedchain.utils import clean_string

from database.chunk.VipsPython.Vips import Vips
from database.custom_embedchain.loaders.base_loader import BaseLoader

@register_deserializable
class WebPageLoader(BaseLoader):
    # def load_data(self, url):
    #     """Load data from a web page."""
    #     # headers = {
    #     #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    #     # }
    #     try:
    #         response = requests.get(url, timeout=5)  # Set timeout to 5 seconds
    #     except requests.Timeout:
    #         print(f"Timeout occurred when fetching data from {url}")
    #         return []
    #     if response.status_code != 200:
    #         print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
    #         return []
    #     data = response.content
    #     soup = BeautifulSoup(data, "lxml")
    #     original_size = len(str(soup.get_text()))

    #     tags_to_exclude = [
    #         "nav",
    #         "aside",
    #         "form",
    #         "header",
    #         "noscript",
    #         "svg",
    #         "canvas",
    #         "footer",
    #         "script",
    #         "style",
    #     ]
    #     for tag in soup(tags_to_exclude):
    #         tag.decompose()

    #     ids_to_exclude = ["sidebar", "main-navigation", "menu-main-menu"]
    #     for id in ids_to_exclude:
    #         tags = soup.find_all(id=id)
    #         for tag in tags:
    #             tag.decompose()

    #     classes_to_exclude = [
    #         "elementor-location-header",
    #         "navbar-header",
    #         "nav",
    #         "header-sidebar-wrapper",
    #         "blog-sidebar-wrapper",
    #         "related-posts",
    #     ]
    #     for class_name in classes_to_exclude:
    #         tags = soup.find_all(class_=class_name)
    #         for tag in tags:
    #             tag.decompose()

    #     content = soup.get_text()
    #     content = clean_string(content)

    #     cleaned_size = len(content)
    #     if original_size != 0:
    #         logging.info(
    #             f"[{url}] Cleaned page size: {cleaned_size} characters, down from {original_size} (shrunk: {original_size-cleaned_size} chars, {round((1-(cleaned_size/original_size)) * 100, 2)}%)"  # noqa:E501
    #         )

    #     meta_data = {
    #         "url": url,
    #     }

    #     return [
    #         {
    #             "content": content,
    #             "meta_data": meta_data,
    #         }
    #     ]

    async def async_load_data(self, url):
        """Load data from a web page asynchronously."""
        timeout = ClientTimeout(20)  # Set total timeout to 20 seconds
        soup = None
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            async with aiohttp.request('GET', url, timeout=timeout, headers=headers) as response:
                if response.status != 200:
                    print(f"Failed to fetch data from {url}. Status code: {response.status}")
                    return
                else:
                    data = await response.text()  # Use response.text() to get string directly
                    if data is None:
                        print(f"Failed to fetch data from {url}. Data is None")
                        return
                    else:
                        soup = BeautifulSoup(data, "lxml")
                        original_size = len(str(soup.get_text()))
        except asyncio.TimeoutError as e:
            print(f"Timeout Error occurred when fetching data from {url}")
        except Exception as e:
            print(f"Error occurred when fetching data from {url}. Error: {e}")


        tags_to_exclude = [
            "nav",
            "aside",
            "form",
            "header",
            "noscript",
            "svg",
            "canvas",
            "footer",
            "script",
            "style",
        ]
        for tag in soup(tags_to_exclude):
            tag.decompose()

        ids_to_exclude = ["sidebar", "main-navigation", "menu-main-menu"]
        for id in ids_to_exclude:
            tags = soup.find_all(id=id)
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
            tags = soup.find_all(class_=class_name)
            for tag in tags:
                tag.decompose()

        content = soup.get_text()
        content = clean_string(content)

        cleaned_size = len(content)
        if original_size != 0:
            logging.info(
                f"[{url}] Cleaned page size: {cleaned_size} characters, down from {original_size} (shrunk: {original_size-cleaned_size} chars, {round((1-(cleaned_size/original_size)) * 100, 2)}%)"  # noqa:E501
            )

        meta_data = {
            "url": url,
        }

        return [
            {
                "content": content,
                "meta_data": meta_data,
            }
        ]

    def load_data(self, url):
        vips = Vips.Vips(urllib.parse.unquote(url, encoding="utf-8"))
        text_groups = vips.parse()
        all_text = ''
        content = []
        for string in text_groups:
            cleaned_string = clean_string(string)
            all_text += cleaned_string
            content.append(cleaned_string)

        meta_data = {
            "url" : url
        }
        # doc_id = hashlib.sha256((all_text + url).encode()).hexdigest()
        return [
            {
                "content": content,
                "meta_data": meta_data,
            }
        ]
