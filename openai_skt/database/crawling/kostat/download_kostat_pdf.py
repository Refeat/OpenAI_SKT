import requests
import json
import os
import threading
from tqdm import tqdm

# Semaphore to limit the number of concurrent threads to 5
semaphore = threading.Semaphore(5)

# 파일 다운로드 함수
def download_file(url, filename, progress):
    # Acquire the semaphore
    with semaphore:
        response = requests.get(url)
        with open(filename, 'wb') as file:
            file.write(response.content)
        progress.update(1)  # tqdm progress 업데이트

def main():
    # JSON 파일 로드
    with open('./updated_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 저장할 폴더가 없으면 생성
    if not os.path.exists('files'):
        os.makedirs('files')

    # tqdm progress bar 설정
    total_files = sum(len(item['attachments']) for item in data)
    with tqdm(total=total_files, desc="Downloading", position=0, leave=True) as progress:
        threads = []

        for item in data:
            for attachment in item['attachments']:
                link = attachment['link']
                name = attachment['name']
                filename = os.path.join('files', name)
                t = threading.Thread(target=download_file, args=(link, filename, progress))
                t.start()
                threads.append(t)

        # 모든 스레드가 완료될 때까지 대기
        for t in threads:
            t.join()

    print("다운로드 완료!")

if __name__ == "__main__":
    main()
