import sys
sys.path.append('../../../') # openai_skt 경로를 sys.path에 추가

from utils import load_api_key

load_api_key()

import json
import asyncio
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp import ClientSession, ClientTimeout

from tqdm import tqdm

from api import KostatAPI

# 한글의 첫 번째 문자와 마지막 문자에 대한 유니코드
FIRST_KOREAN = 44032  # '가'
LAST_KOREAN = 55203   # '힣'

sem = asyncio.Semaphore(3)
data_lock = asyncio.Lock()

combined_results = []
failed_chars = []  # 처리하지 못한 문자들을 저장하기 위한 리스트

def write_to_file(combined_results):
    with open("results111.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(combined_results, ensure_ascii=False, indent=4))

async def write_completed_character_to_file(char):
    async with data_lock:  # 동일한 데이터 잠금을 사용하여 파일 동시 쓰기를 방지합니다.
        with open("completed_characters.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(char, ensure_ascii=False))
            f.write(",\n")

async def search_character(kostat_api, char, pbar):
    startCount = 0
    retries = 3

    async with sem:
        while retries > 0:
            try:
                result = await kostat_api.async_search(char, top_k=10, startCount=startCount)
                retries = 0  # reset retries if the request is successful
            except ClientConnectorError as e:
                print(f"Error for character {char}: {e}")
                failed_chars.append(char)
                break
            except TimeoutError:
                retries -= 1
                if retries <= 0:
                    print(f"Timeout for character {char}. All retries exhausted.")
                    failed_chars.append(char)
                else:
                    print(f"Timeout for character {char}. Retrying ({3 - retries}/3)...")
                continue

            for item in result:
                combined_results.append(item)
            
            if len(result) < 10:
                await write_completed_character_to_file(char)
                break
            elif len(result) == 10:
                startCount += 10
    pbar.update(1)

async def main():
    kostat_api = KostatAPI(category='통계청누리집')

    tasks = []
    pbar = tqdm(total=(LAST_KOREAN - FIRST_KOREAN + 1), desc="Processing characters", unit="char")

    for unicode in range(FIRST_KOREAN, LAST_KOREAN + 1):
        char = chr(unicode)
        if len(char) == 1:
            task = asyncio.ensure_future(search_character(kostat_api, char, pbar))
            tasks.append(task)
    
    await asyncio.gather(*tasks)
    pbar.close()
    write_to_file(combined_results)

if __name__ == "__main__":
    asyncio.run(main())

    # Print failed characters
    if failed_chars:
        print("Failed characters:", ", ".join(failed_chars))