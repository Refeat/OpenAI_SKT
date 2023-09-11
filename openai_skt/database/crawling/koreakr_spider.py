import os
import re
import json
import argparse
import logging
from urllib.parse import urljoin

import scrapy
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.http import HtmlResponse
from scrapy.crawler import CrawlerProcess

from scrapy.pipelines.files import FilesPipeline

class MyFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        # 아이템에서 파일 이름을 가져옵니다.
        file_name = request.meta['item']['pdf_path']  # 이미 파일 이름이 있으므로 다시 분할할 필요가 없습니다.
        print('-'*30)
        print(file_name)
        return file_name  # 파일 확장자가 이미 포함되어 있으므로 추가로 설정할 필요가 없습니다.

class KoreaKrItem(scrapy.Item):
    web_page_link = scrapy.Field()
    pdf_download_link = scrapy.Field()
    file_urls = scrapy.Field()  # 다운로드할 파일 URL 목록
    pdf_path = scrapy.Field()

class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open('output.json', 'w', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

class SeleniumRequest(scrapy.Request):
    def __init__(self, url, callback, meta=None, *args, **kwargs):
        super().__init__(url, callback=callback, meta=meta, *args, **kwargs)

class SeleniumMiddleware():
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def process_request(self, request, spider):
        if isinstance(request, SeleniumRequest):
            self.driver.get(request.url)
            body = self.driver.page_source
            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

    def spider_closed(self):
        self.driver.quit()

class KoreaKrSpider(scrapy.Spider):
    name = 'koreakr_spider'

    def __init__(self, crawler_type='scrapy', start_url=None, base_url=None, *args, **kwargs):
        super(KoreaKrSpider, self).__init__(*args, **kwargs)
        self.crawler_type = crawler_type
        self.start_urls = [start_url]
        self.base_url = base_url
        if self.crawler_type == 'selenium':
            self.custom_settings = {
                'FILES_STORE': 'downloads',
                'ITEM_PIPELINES': {'__main__.MyFilesPipeline': 1},
                'DOWNLOADER_MIDDLEWARES': {
                    '__main__.SeleniumMiddleware': 800,
                },
                'DOWNLOAD_DELAY': 2,
            }

    def start_requests(self):
        if self.crawler_type == 'selenium':
            for url in self.start_urls:
                yield SeleniumRequest(url, self.parse)
        else:
            for url in self.start_urls:
                yield scrapy.Request(url, self.parse)

    def parse(self, response):
        for link in response.css('div.list_type ul li a::attr(href)').extract():
            if self.crawler_type == 'selenium':
                absolute_link = urljoin(self.base_url, link)
                yield SeleniumRequest(absolute_link, callback=self.parse_detail)
            else:
                absolute_link = urljoin(self.base_url, link)
                yield scrapy.Request(absolute_link, callback=self.parse_detail)

        next_page = response.css('div.paging a.next::attr(onclick)').re_first(r'pageLink\((\d+)\)')
        if next_page and int(next_page) <= 10:  # 10페이지까지만 크롤링합니다.
            next_url = urljoin(self.base_url, f'/briefing/pressReleaseList.do?pageIndex={next_page}')
            if self.crawler_type == 'selenium':
                yield SeleniumRequest(next_url, self.parse) 
            else:
                yield scrapy.Request(next_url, self.parse)



    def parse_detail(self, response):
        # PDF 파일과 HWPX 파일 링크를 모두 찾는다.
        file_links = response.css('div.filedown a::attr(href)').extract()
        file_names = response.css('div.filedown a::text').extract()  # 파일 이름을 가져옵니다.
        file_types = response.css('div.filedown img::attr(alt)').extract()

        # 우선 PDF 파일의 링크를 찾는다.
        download_link = None
        download_name = None
        for link, name, ftype in zip(file_links, file_names, file_types):
            if "PDF파일" in ftype:
                download_link = link
                download_name = name.strip()  # 앞뒤 공백 제거
                break
        # PDF 링크가 없다면, HWPX 파일의 링크를 찾는다.
        if not download_link:
            for link, name, ftype in zip(file_links, file_names, file_types):
                if "한글파일" in ftype:
                    download_link = link
                    download_name = name.strip()  # 앞뒤 공백 제거
                    break
        # link를 찾았다면 base_url을 붙여서 완전한 URL로 만들어준다.
        if download_link:
            download_link = urljoin(self.base_url, download_link)
            download_name = re.sub(r'[\/:*?"<>|]', '_', download_name)  # 정규식을 사용하여 대체
            download_name = download_name.replace(' ', '_')  # 띄어쓰기를 "_"로 대체
        else:
            download_name = None  # link를 찾지 못했다면 download_name도 None으로 설정한다.

        file_id = re.search(r'fileId=(\d+)', download_link)
        tbl_key = re.search(r'tblKey=(\w+)', download_link)

        if file_id and tbl_key:
            # 직접 파일 다운로드 URL을 생성합니다.
            download_link = f'https://www.korea.kr/common/download.do?fileId={file_id.group(1)}&tblKey={tbl_key.group(1)}'
        else:
            download_link = None  # 파일 다운로드 링크가 없으면 None으로 설정

        yield KoreaKrItem(
            web_page_link=response.url,
            pdf_download_link=download_link,
            file_urls=[download_link] if download_link else [],
            pdf_path=download_name  # download_name을 여기에 설정
        )




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run KoreaKrSpider")
    parser.add_argument('--base_url', default="https://www.korea.kr/", help="Base URL to crawl")
    parser.add_argument('--start_url', default="https://www.korea.kr/briefing/pressReleaseList.do", help="Start URL to crawl")
    parser.add_argument('--output_dir', default='../../db/koreakr', help="Directory to save output")
    parser.add_argument('--crawler', default='scrapy', choices=['scrapy', 'selenium'], help="Crawler type to use")
    args = parser.parse_args()

    # logger = logging.getLogger("spider")
    # logger.debug("start")
    
    KoreaKrSpider.custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'FILES_STORE': args.output_dir,
        'ITEM_PIPELINES': {
            '__main__.MyFilesPipeline': 1,
            # 'scrapy.pipelines.files.FilesPipeline': 1,
            '__main__.JsonWriterPipeline': 2,
        },
    }

    if args.crawler == 'selenium':
        KoreaKrSpider.custom_settings.update({
            'DOWNLOADER_MIDDLEWARES': {
                '__main__.SeleniumMiddleware': 800,
            },
            'DOWNLOAD_DELAY': 2,
        })


    process = CrawlerProcess(KoreaKrSpider.custom_settings)
    process.crawl(KoreaKrSpider, crawler_type=args.crawler, base_url=args.base_url, start_url=args.start_url)
    process.start()
