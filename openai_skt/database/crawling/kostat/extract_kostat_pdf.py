import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
import threading

sem = threading.Semaphore(5)  # Limit to 5 tasks at a time
file_lock = threading.Lock()  # Lock for file writing

def fetch(url):
    with sem:
        response = requests.get(url)
        return response.text

def process_data(item, progress):  # Accept progress bar as an argument
    url = item["data_path"]
    response_text = fetch(url)
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

    # Save to the new JSON file
    with file_lock:
        with open('updated_data.json', 'a', encoding='utf-8') as outfile:
            json.dump(item, outfile, ensure_ascii=False, indent=4)
            outfile.write(",\n")  # add comma and newline for separation

    progress.update(1)

def main():
    # Load JSON data from the file
    with open('output.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Initialize the output file with an empty JSON array
    with open('updated_data.json', 'w', encoding='utf-8') as outfile:
        outfile.write("[\n")

    # Create a tqdm progress bar and process data
    with tqdm(total=len(data), desc="Processing", position=0, leave=True) as progress:
        
        threads = []
        for item in data:
            t = threading.Thread(target=process_data, args=(item, progress))
            t.start()
            threads.append(t)

        # Wait for all threads to complete
        for t in threads:
            t.join()

    # Finalize the JSON array in the output file
    with open('updated_data.json', 'rb+') as outfile:
        outfile.seek(-2, 2)  # Move cursor 2 bytes before the end
        outfile.truncate()   # Remove the last comma and newline
        outfile.write(b"\n]")

    print("처리 완료!")

main()