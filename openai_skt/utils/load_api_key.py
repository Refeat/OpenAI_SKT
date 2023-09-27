import os
import configparser

def load_api_key():
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    secrets_path = os.path.join(current_directory, '../../.secrets.ini')
    config = configparser.ConfigParser()
    config.read(secrets_path)

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