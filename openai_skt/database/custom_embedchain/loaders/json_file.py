import os
import json
import copy

from pdfminer.high_level import extract_pages
from embedchain.helper_classes.json_serializable import register_deserializable

from database.custom_embedchain.loaders.base_loader import BaseLoader

@register_deserializable
class JsonFileLoader(BaseLoader):
    def load_data(self, url):
        """Load data from a PDF file."""
        with open(url, 'r') as f:
            json_data = json.load(f)

        pages = extract_pages(json_data['url'])
        output = []
        meta_data = {}
        meta_data["url"] = json_data['name']
        meta_data["path"] = json_data['url'] # 실제 경로
        meta_data["data_type"] = 'pdf_file'
        for idx, (data, page) in enumerate(zip(json_data['content'], pages)):
            single_meta_data = copy.deepcopy(meta_data)
            single_meta_data["page"] = idx+1
            single_meta_data["image_path"] = data[0]["image_path"]
            output.append(
                {
                    "content": page,
                    "meta_data": single_meta_data,
                    "image": data, # 각 페이지의 이미지
                }
            )
        return output