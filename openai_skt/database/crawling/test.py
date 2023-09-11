import requests
import os

def download_file(url, save_path):
    response = requests.get(url)
    response.raise_for_status()
    with open(save_path, 'wb') as file:  # 'wb'는 binary mode로 파일을 엽니다.
        file.write(response.content)  # response.content는 binary content를 반환합니다.

# 사용 예제
url = 'https://www.korea.kr/common/download.do?fileId=197458705&tblKey=GMN'
save_path = os.path.join('.', '[23-826](보도자료) 박진 외교장관, 『엘리자베스 살몬』와 북한인권 특별보고관 만남.pdf')
download_file(url, save_path)
