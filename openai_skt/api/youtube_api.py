import configparser

config = configparser.ConfigParser()
config.read('../.secrets.ini')
YOUTUBE_KEY = config['YOUTUBE']['YOUTUBE_API_KEY']

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser

from api.base import BaseAPI

class YoutubeAPI(BaseAPI):
    # 유튜브 API
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.youtube.com/'
        self.name = 'youtube'
        self.youtube_api = build("youtube", "v3", developerKey=YOUTUBE_KEY)

    def search(self, query:str, top_k:int = 5):
        response = self.youtube_api.search().list(
            q = query,
            order = 'relevance',
            part = 'snippet',
            maxResults = top_k
        ).execute()
        return self.parse_result(response)

    async def async_search(self, query:str, top_k:int = 5):
        return self.search(query, top_k)

    def parse_result(self, result):
        ret = []
        for item in result['items']:
            if item['id']['kind'] == 'youtube#video':
                ret.append({
                    '제목': item['snippet']['title'],
                    '날짜': item['snippet']['publishTime'],
                    '채널': item['snippet']['channelTitle'],
                    '설명': item['snippet']['description'],
                    '링크': 'https://www.youtube.com/watch?v=' + item['id']['videoId'],
                    'data_type': 'youtube_video',
                    'data_path': 'https://www.youtube.com/watch?v=' + item['id']['videoId'],
                })
        return ret

    async def async_parse_result(self, result):
        return self.parse_result(result)