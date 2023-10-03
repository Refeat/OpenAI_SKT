import os
import sys
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
sys.path.append(os.path.join(current_directory, '../../../openai_skt'))
### Set OpenAI key 
import os
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(current_directory, '../../../.secrets.ini'))
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

import os
from tqdm import tqdm

import os
from database import DataBase, CustomEmbedChain
from tqdm import tqdm
from database.pre_embedding.layout_parser import LayoutModel
from multiprocessing import Pool, Lock

def initialize_model(domain):
    layout_model = LayoutModel()
    layout_model.set_domain(domain)
    return layout_model

def layout_process_file(args):
    file, domain = args
    layout_model = initialize_model(domain)
    layout_model(file)
    return f"Processed {file}"

lock = Lock()
embed_chain = CustomEmbedChain()
db = DataBase(files=[], embed_chain=embed_chain)

def layout_process_files(pdf_files=None, num_processes=8, domain=None):
    # Prepare inputs for multiprocessing
    inputs = [(file, domain) for file in pdf_files]

    completed_count = 0

    def callback(result):
        nonlocal completed_count
        completed_count += 1
        if completed_count % 10 == 0:  # Adjust this for frequency of progress update
            print(f"Processed {completed_count}/{len(pdf_files)} files")

    with Pool(num_processes) as pool:
        for result in pool.imap_unordered(layout_process_file, inputs):
            callback(result)


def embed_process_files(json_files=None, domain=None):
    # Prepare inputs for multiprocessing
    db.pre_add_files(json_files, domain)
    


# 이 코드는 반드시 db를 생성하고자 하는 위치 아래에서 실행해야함.
if __name__ == "__main__":
    data_root_path = "/root/data/"
    domain = "kostat"
    
    json_root_path = "/root/OpenAI_SKT/openai_skt/data"
    json_root_path = os.path.join(json_root_path, domain, "json")
    os.makedirs(json_root_path, exist_ok=True)
    json_files = os.listdir(json_root_path)
    
    # Convert list of json_files to a set of filenames without the .json extension
    json_filenames_set = {os.path.basename(json_file).replace('.json', '') for json_file in json_files}

    # Generate pdf_files and filter out those that have corresponding JSONs in json_filenames_set
    pdf_files = [os.path.join(data_root_path, domain, pdf_file) 
                 for pdf_file in os.listdir(os.path.join(data_root_path, domain))[:12] 
                 if pdf_file.endswith('.pdf') and os.path.basename(pdf_file).replace('.pdf', '') not in json_filenames_set]
    print("process pdf files", pdf_files)
    layout_process_files(pdf_files=pdf_files, num_processes=8, domain=domain)
    
    # Generate the list of json_files with their paths and type "json_file"
    json_files = [(os.path.join(json_root_path, f), "json_file") for f in json_files if f.endswith('.json')]
    print("process json file", json_files)

    embed_process_files(json_files=json_files, domain=domain)