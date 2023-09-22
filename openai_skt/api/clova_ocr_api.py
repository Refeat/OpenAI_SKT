import os

try:
    try:
        CLOVA_OCR_API_KEY = os.environ['CLOVA_OCR_API_KEY']
    except:
        import configparser

        config = configparser.ConfigParser()
        current_path = os.path.abspath(os.path.dirname(__file__))
        secrets_path = os.path.join(current_path, '../../.secrets.ini')
        config.read(secrets_path)
        CLOVA_OCR_API_KEY = config['NAVER']['CLOVA_OCR_API_KEY']
except:
    from django.conf import settings
    config = settings.KEY_INFORMATION
    CLOVA_OCR_API_KEY = config['NAVER']['CLOVA_OCR_API_KEY']

import json
import requests
import uuid
import time

import cv2
import numpy as np

class ClovaOCRAPI:
    def __init__(self):
        self.api_key = CLOVA_OCR_API_KEY
        self.api_url = "https://40s1tdjs0r.apigw.ntruss.com/custom/v1/23456/aa9d4447014b5f6ff61370acfd70e0f5677dc1674c95fde605a9b627e10f70f7/general"

    def concatenate_text_from_json(self, json_data):
        concatenated_text = ""
        for image in json_data.get('images', []):
            for field in image.get('fields', []):
                infer_text = field.get('inferText', '')
                concatenated_text += infer_text + ' '
        return concatenated_text

    def get_text(self, image_input):
        if isinstance(image_input, str):
            # Get the file extension and use it as the format
            file_extension = os.path.splitext(image_input)[1][1:].lower()
            image_data = open(image_input, 'rb')
        elif isinstance(image_input, np.ndarray):
            file_extension = 'jpg'  # Assuming JPEG format for NumPy array
            is_success, im_buf_arr = cv2.imencode(".jpg", image_input)
            if not is_success:
                print("Error encoding the image to byte stream")
                return ''
            image_data = bytes(im_buf_arr)
        else:
            print("Unsupported input type")
            return ''

        request_json = {
            'images': [
                {
                    'format': file_extension,
                    'name': 'demo'
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }

        payload = {'message': json.dumps(request_json).encode('UTF-8')}
        files = [('file', image_data)]
        headers = {'X-OCR-SECRET': self.api_key}
        response = requests.request("POST", self.api_url, headers=headers, data=payload, files=files)

        if response.status_code == 200:
            res = json.loads(response.text.encode('utf8'))
            concatenated_text = self.concatenate_text_from_json(res)
            return concatenated_text
        else:
            print(f"Error: {response.status_code}")
            return ''


if __name__ == '__main__':
    clova_ocr_api = ClovaOCRAPI()
    print(clova_ocr_api.get_text('/root/OpenAI_SKT/openai_skt/tutorials/test_data/test20.png'))