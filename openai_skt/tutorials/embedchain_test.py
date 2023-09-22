import sys
sys.path.append('..')
### Set OpenAI key 
import os
import configparser

config = configparser.ConfigParser()
config.read('../../.secrets.ini')
OPENAI_API_KEY = config['OPENAI']['OPENAI_API_KEY']
YOUTUBE_KEY = config['YOUTUBE']['YOUTUBE_API_KEY']
NAVER_CLIENT_ID = config['NAVER']['NAVER_CLIENT_ID']
NAVER_CLIENT_SECRET = config['NAVER']['NAVER_CLIENT_SECRET']
GOOGLE_SEARCH_KEY = config['GOOGLE']['GOOGLE_API_KEY']
CSE_ID = config['GOOGLE']['CSE_ID']
SERPAPI_API_KEY = config['SERPAPI']['SERPAPI_API_KEY']


os.environ.update({'OPENAI_API_KEY': OPENAI_API_KEY})
os.environ.update({'YOUTUBE_KEY': YOUTUBE_KEY})
os.environ.update({'NAVER_CLIENT_ID': NAVER_CLIENT_ID})
os.environ.update({'NAVER_CLIENT_SECRET': NAVER_CLIENT_SECRET})
os.environ.update({'GOOGLE_SEARCH_KEY': GOOGLE_SEARCH_KEY})
os.environ.update({'CSE_ID': CSE_ID})
os.environ.update({'SERPAPI_API_KEY': SERPAPI_API_KEY})
from database import CustomEmbedChain
embedchain = CustomEmbedChain()
# embedchain.add('https://namu.wiki/w/%EB%82%98%EB%AC%B4%EC%9C%84%ED%82%A4:%EB%8C%80%EB%AC%B8', 'web_page') # webpage
# embedchain.add('https://www.youtube.com/watch?v=a8uPDppckQk', 'youtube_video') # youtube
# embedchain.add('./test_data/X2Download.app - 월세=월급, 미친 집값의 나라에서 한국인이 발견한 기회 _ 고투조이 변성민 (128 kbps).mp3', 'audio') # audio
embedchain.add('/root/OpenAI_SKT/openai_skt/tutorials/test_data/(보도자료) 제20회 전국학생통계활용대회 결과 발표.pdf', 'pdf_file') # pdf