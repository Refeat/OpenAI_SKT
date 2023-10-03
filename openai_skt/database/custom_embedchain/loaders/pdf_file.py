from langchain.document_loaders import PyPDFLoader
from pdf2image import convert_from_path
from pdfminer.high_level import extract_pages

from embedchain.helper_classes.json_serializable import register_deserializable
# from embedchain.loaders.base_loader import BaseLoader
from embedchain.utils import clean_string

from database.custom_embedchain.loaders.base_loader import BaseLoader
from database.custom_embedchain.chunkers.new_layout_parser import LayoutModel

layout_model = LayoutModel()
layout_model.set_domain("others")

@register_deserializable
class PdfFileLoader(BaseLoader):
    def load_data(self, url):
        """Load data from a PDF file."""
        # loader = PyPDFLoader(url)
        # pages = loader.load_and_split()
        pages = extract_pages(url)
        # images = convert_from_path(url)
        image_layout_results = layout_model(url)
        # 이미지 변환
        output = []

        for idx, (image_layout, page) in enumerate(zip(image_layout_results, pages)):
            meta_data = {}
            meta_data["url"] = url
            meta_data["page"] = idx+1
            meta_data["data_type"] = 'pdf_file'
            output.append(
                {
                    "content": page,
                    "meta_data": meta_data,
                    "image": image_layout, # 각 페이지의 이미지
                }
            )
        return output