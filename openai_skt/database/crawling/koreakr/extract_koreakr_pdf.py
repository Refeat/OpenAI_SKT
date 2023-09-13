import os
import re
import json
import aiohttp
import asyncio
import argparse

from tqdm import tqdm

sem = asyncio.Semaphore(10) # Limit the number of concurrent downloads

async def extract_filename_from_content_disposition(content_disposition):
    filename_match = re.search(r'filename\*=UTF-8\'\'(.+)', content_disposition)
    if filename_match:
        filename = aiohttp.helpers.parse_mimetype(filename_match.group(1)).decode('utf-8')
        return sanitize_filename(filename)
    filename_match = re.search(r'filename="(.+)"', content_disposition)
    if filename_match:
        try:
            filename = filename_match.group(1).encode('ISO-8859-1').decode('utf-8')
            return sanitize_filename(filename)
        except:
            filename = filename_match.group(1)
            return sanitize_filename(filename)
    return None

def sanitize_filename(filename):
    invalid_chars = "\\/:*?\"<>|"
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename

async def download_file(data, download_folder, pbar):
    url = data.get("pdf_download_link")
    downloaded_files = []
    
    async with sem:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    # print(f"Failed to download {url}. HTTP status code: {response.status}")
                    pass
                
                content_disposition = response.headers.get("Content-Disposition")
                if not content_disposition:
                    # print(f"{url}, Content-Disposition header not found")
                    return []  # Return an empty list for this url

                filename = await extract_filename_from_content_disposition(content_disposition)
                if not filename:
                    # print(f"{url}, Filename not found in Content-Disposition header")
                    return []  # Return an empty list for this url
                
                if not (filename.endswith('.pdf') or filename.endswith('.hwpx')):
                    # print(f"Skipping {url} due to unsupported file format: {filename}")
                    return []  # Return an empty list for this url

                filepath = os.path.join(download_folder, filename)
                with open(filepath, 'wb') as file:
                    file.write(await response.read())

                # Dictionary with web_page_link, pdf_download_link, and the downloaded file's path
                downloaded_files.append({
                    "web_page_link": data.get("web_page_link"),
                    "pdf_download_link": url,
                    "downloaded_file_path": filepath
                })
                
                pbar.update(1)

    return downloaded_files

def read_json_input(json_filepath):
    data_list = []
    with open(json_filepath, 'r', encoding='utf-8') as json_file:
        for line in json_file:
            data = json.loads(line.strip())
            data_list.append(data)
    return data_list

def save_results_to_json(downloaded_files, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        for file_info_list in downloaded_files:
            if file_info_list:  # Check if the list is not empty
                for file_info in file_info_list:  # Iterate through the list and save individual dictionaries
                    json.dump(file_info, output_file, ensure_ascii=False)
                    output_file.write('\n')

async def main(json_filepath, download_folder, output_filename):
    os.makedirs(download_folder, exist_ok=True)
    tasks = []
    
    data_list = read_json_input(json_filepath)
    
    with tqdm(total=len(data_list), desc="Downloading", dynamic_ncols=True) as pbar:
        for data in data_list:
            tasks.append(download_file(data, download_folder, pbar))

        downloaded_files = await asyncio.gather(*tasks)

    save_results_to_json(downloaded_files, output_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download PDFs from JSON file.')
    parser.add_argument('--json_filepath', type=str, help='Path to the JSON file containing download links.', default='koreakr.json')
    parser.add_argument('--download_folder', type=str, help='Folder to save downloaded PDFs.', default='files')
    parser.add_argument('--output_filename', type=str, help='Filename for the JSON file to save the results inside the download_folder.', default='downloaded_files.json')

    args = parser.parse_args()
    asyncio.run(main(args.json_filepath, args.download_folder, args.output_filename))
