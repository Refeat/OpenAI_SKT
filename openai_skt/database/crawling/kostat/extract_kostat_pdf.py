import requests
from bs4 import BeautifulSoup
import json

# results.json 파일에서 데이터 불러오기
with open('results.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# data_path 추출
urls = [item["data_path"] for item in data]

for item in data:
    url = item["data_path"]
    
    # 해당 URL에 대한 요청
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 첨부파일 링크 추출
    attachment_links = soup.select(".bvf_name")
    
    # 첨부파일 링크 리스트 생성
    attachments = []
    for link in attachment_links:
        attachments.append("https://kostat.go.kr" + link['href'])
        
    # 원래 JSON 데이터에 첨부파일 링크 추가
    item["attachments"] = attachments

# 새로운 JSON 파일로 저장
with open('updated_data.json', 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=4)

print("처리 완료!")
