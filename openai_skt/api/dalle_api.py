import os

try:
    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    except:
        import configparser

        config = configparser.ConfigParser()
        config.read('../../.secrets.ini')
        OPENAI_API_KEY = config['OPENAI']['OPENAI_API_KEY']
except:
    from django.conf import settings
    config = settings.KEY_INFORMATION
    OPENAI_API_KEY = config['OPENAI']['OPENAI_API_KEY']

import openai

class DalleAPI:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY

    def generate_image(self, image_caption: str) -> str:
        image_url = None
        try:
            response = openai.Image.create(
                prompt=image_caption,
                n=1,
                size="256x256",
            )
            image_url = response["data"][0]["url"]
        except Exception as e:
            print(f"An error occurred: {e}")
        return image_url

if __name__ == '__main__':
    dalle_api = DalleAPI()
    image_url = dalle_api.generate_image("A drawing of a bag")
    print(image_url)