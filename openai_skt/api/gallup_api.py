import asyncio
import urllib
import requests

import aiohttp
from bs4 import BeautifulSoup

try:
    from api.base import BaseAPI
except ImportError:
    from base import BaseAPI


class GallupAPI(BaseAPI):
    # 갤럽 API
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.gallup.co.kr/'
        self.search_url = self.base_url + 'etc/SearchReport.asp'
        self.name = 'gallup'

    def search(self, query, target='1', top_k:int = 5):
        data, headers = self.parse_input(query, target)

        response = requests.post(self.search_url, data=data, headers=headers)
        
        if response.status_code == 200:
            html_content = response.text
            search_results = self.parse_result(html_content)
            return search_results[:top_k]
        else:
            print('갤럽 API 검색 요청에 실패하였습니다.')
            return []

    async def async_search(self, query, target='1', top_k:int = 5):
        data, headers = self.parse_input(query, target)

        async with aiohttp.ClientSession() as session:
            async with session.post(self.search_url, data=data, headers=headers) as response:
                html_content = await response.text()
                search_results = self.parse_result(html_content)
                return search_results[:top_k]

    def parse_input(self, query, target='1'):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ko,ko-KR;q=0.9,en;q=0.8,en-US;q=0.7,en-GB;q=0.6,ja;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            # 쿠키가 변할 수 있음. 에러발생시 쿠키를 확인하고 수정해주세요.
            "Cookie": "_gid=GA1.3.916308141.1693380110; ASPSESSIONIDAGRRTQDB=GNEKDIEDNIGAALHIDKJPNPFO; _ga=GA1.1.2053665757.1693289581; _ga_MGLX1H2HFS=GS1.1.1693380109.3.1.1693382478.0.0.0",
            "Host": "www.gallup.co.kr",
            "Origin": "https://www.gallup.co.kr",
            "Referer": "https://www.gallup.co.kr/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }
        
        # 검색 폼 데이터
        data = {
            'search_target': target,  # '1'은 갤럽리포트, '2'는 웹사이트
            'search_query':  urllib.parse.quote(query.encode('euc-kr'))
        }
        return data, headers

    def parse_result(self, html_result):
        soup = BeautifulSoup(html_result, 'lxml')
        
        # Extract necessary information based on the website's structure
        # 검색 결과 항목을 저장할 리스트
        search_results = []

        # 각 row를 순회하며 정보 추출
        for row in soup.select('.tbl01 .row'):
            attachment_link = row.select_one('.t04 a')
            number = row.select_one('.t01').get_text(strip=True)
            title = row.select_one('.t02 a').get_text(strip=True)
            date = row.select_one('.t03').get_text(strip=True)
            file_link = self.base_url + attachment_link['href'] if attachment_link else None
            url = f'https://www.gallup.co.kr/gallupdb/reportContent.asp?seqNo={number}'
            
            result = {
                # '번호': number,
                'title': title,
                # '날짜': date,
                # '첨부파일': file_link,
                # '링크': url,
                'description': title,
                'data_type': 'pdf_file',
                'data_path': file_link
            }
            search_results.append(result)

        return search_results

if __name__ == "__main__":
    gallup_api = GallupAPI()
    # Using asyncio to run the async function
    result = asyncio.run(gallup_api.async_search('부동산'))
    print(result)
