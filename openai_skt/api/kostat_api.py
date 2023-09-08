import re
import asyncio
import urllib
import requests

import aiohttp
from bs4 import BeautifulSoup

try:
    from api.base import BaseAPI
except ImportError:
    from base import BaseAPI

class KostatAPI(BaseAPI):
    # 통계청 API
    # 검색 카테고리: 통계청누리집, 지표누리, 국가통계포털(KOSIS)통계표, 온라인간행물, 통계설명자료, 통계용어
    # 여기서는 국가통계포털(KOSIS)통계표 검색만 구현
    def __init__(self):
        super().__init__()
        self.base_url = 'https://kostat.go.kr/'
        self.search_url = self.base_url + 'unifSearch/search.es'
        self.name = 'kostat'
        self.schema_name_list = ['제목', '날짜', '설명', '링크', 'data_type', 'data_path']

    def search(self, query, top_k:int = 5):
        data, headers = self.parse_input(query)

        response = requests.post(self.search_url, data=data, headers=headers)
        
        if response.status_code == 200:
            html_content = response.text
            search_results = self.parse_result(html_content)
            return search_results[:top_k]
        else:
            print('통계청 API 검색 요청에 실패하였습니다., status_code:', response.status_code)
            return []
    
    async def async_search(self, query, top_k:int = 5):
        
        data, headers = self.parse_input(query)

        async with aiohttp.ClientSession() as session:
            async with session.post(self.search_url, data=data, headers=headers) as response:
                html_content = await response.text()
                search_results = self.parse_result(html_content)
                return search_results[:top_k]

    def parse_result(self, result):
        soup = BeautifulSoup(result, 'lxml')

        search_results = []

        # 각 항목(리스트 아이템)을 순회
        for li in soup.select('div.gsb_list.srh_rlist > ul > li'):
            title = li.select_one('a.gsbl_link').text.replace('<!--HS-->', '').replace('<!--HE-->', '').strip()
            institute_period = li.select_one('p.gsbl_info').text.strip()
            description = li.select_one('p.gsbl_descript').text.strip()
            javascript_url = li.select_one('a.gsbl_link')['href']
            url = self.parse_url(javascript_url)

            # 결과 저장
            search_results.append({
                'title': title,
                # '날짜': institute_period,
                'description': description,
                # '링크': url,
                'data_type': 'web_page',
                'data_path': url
            })
        return search_results
    
    def parse_url(self, url):
        parameters = re.findall(r"'(.*?)'", url)

        # 파라미터에 맞게 매핑
        orgId = parameters[0]
        tblId = parameters[1]
        path = parameters[3]
        vw_cd = parameters[4]
        list_id = parameters[5]

        base_url = "https://kosis.kr/statHtml/statHtml.do"
        params = {
            "orgId": orgId,
            "tblId": tblId,
            "vw_cd": vw_cd,
            "list_id": list_id,
            "scrId": "",
            "seqNo": "",
            "lang_mode": "ko",
            "obj_var_id": "",
            "itm_id": "",
            "conn_path": "K1",
            "path": urllib.parse.quote(path)
        }

        return base_url + "?" + urllib.parse.urlencode(params)
    
    def parse_input(self, query):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ko,ko-KR;q=0.9,en;q=0.8,en-US;q=0.7,en-GB;q=0.6,ja;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "",
            "Host": "kostat.go.kr",
            "Origin": "https://kostat.go.kr",
            "Referer": "https://kostat.go.kr/unifSearch/search.es",
            "Sec-Ch-Ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }
        
        # Create payload (reduced to only the essentials, as you provided before)
        data = {
            'start': 0,
            'start1': 0,
            'count': 10,
            'startCount': 0,
            'startCount1': 0,
            'startDate': '',
            'endDate': '',
            'viewCount': 0,
            'viewContent': 'Y',
            'range': '',
            'subCol': 'ALL',
            'sort': 'DATE,1',
            'sortField': 'RANK,1',
            'searchOption': '',
            'divField': '',
            'datesearch': 'no',
            'requery': '',
            'lastquery': query,
            'detailSearchf': 'N',
            'subjectSearch': '',
            'synYN': 'Y',
            'searchField': '',
            'openDivClass3': '',
            'cookie': '000',
            'jopage': 1,
            'arkChk': 'Y',
            'YstartTmp': '',
            'MstartTmp': '',
            'DstartTmp': '',
            'YendTmp': '',
            'MendTmp': '',
            'DendTmp': '',
            'sortCondition': '',
            'searchFieldCondition': '',
            'termsCondition': '',
            'viewcountCondition': '',
            'statDBsearchField1': 1,
            'statDBsearchField2': 1,
            'statDBsearchField3': 1,
            'statDBsearchField4': 1,
            'statDBsearchField5': 1,
            'webCheckbox1': '',
            'webCheckbox2': '',
            'webCheckbox3': '',
            'webCheckbox4': '',
            'webCheckbox5': '',
            'webCheckbox6': '',
            'webCheckbox7': '',
            'webCheckbox8': '',
            'webCheckbox9': '',
            'webCheckbox10': '',
            'webCheckbox11': '',
            'webCheckbox12': '',
            'webCheckbox13': '',
            'hireCheckbox1': '',
            'hireCheckbox2': '',
            'hireCheckbox3': '',
            'hireCheckbox4': '',
            'hireCheckbox5': '',
            'hireCheckbox6': '',
            'hireCheckbox7': '',
            'hireCheckbox8': '',
            'hireCheckbox9': '',
            'collection': 'statDB',
            'statId': '',
            'orgCode': '',
            'select_search': 'statDB',
            'query': query
        }

        return data, headers
    
if __name__ == "__main__":
    kostat_api = KostatAPI()
    # Using asyncio to run the async function
    result = asyncio.run(kostat_api.async_search('부동산'))
    print(result)
