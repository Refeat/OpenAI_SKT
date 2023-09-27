import aiohttp
import asyncio
import aiofiles
from bs4 import BeautifulSoup
import json
from tqdm import tqdm

async def fetch(url, session):
    async with session.get(url) as response:
        return await response.text()

async def process_data(item, session):
    url = item["data_path"]
    response_text = await fetch(url, session)
    soup = BeautifulSoup(response_text, 'html.parser')

    # 첨부파일 링크 추출
    pdf_file = soup.find('a', href=True, string=lambda t: t and t.endswith('.pdf'))

    # PDF 파일이 없을 경우 HWP 또는 HWPX 파일 찾기
    if not pdf_file:
        hwp_file = soup.find('a', href=True, string=lambda t: t and (t.endswith('.hwp') or t.endswith('.hwpx')))
        attachment_links = [hwp_file] if hwp_file else []
    else:
        attachment_links = [pdf_file]

    # 첨부파일 링크 및 이름 리스트 생성
    attachments = []
    for link in attachment_links:
        file_link = "https://kostat.go.kr" + link['href']
        file_name = link.text
        attachments.append({"link": file_link, "name": file_name})

    # 원래 JSON 데이터에 첨부파일 링크 추가
    item["attachments"] = attachments

    return item

async def main():
    # results.json 파일에서 데이터 불러오기
    async with aiofiles.open('output.json', 'r', encoding='utf-8') as file:
        data = await file.read()
        data = json.loads(data)

    async with aiohttp.ClientSession() as session:
        processed_data = await asyncio.gather(*[process_data(item, session) for item in tqdm(data)])

    # 새로운 JSON 파일로 저장
    async with aiofiles.open('updated_data.json', 'w', encoding='utf-8') as outfile:
        await outfile.write(json.dumps(processed_data, ensure_ascii=False, indent=4))

    print("처리 완료!")

asyncio.run(main())
