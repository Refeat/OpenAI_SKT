from langchain.document_loaders import PyPDFLoader
from pdf2image import convert_from_path
from pdfminer.high_level import extract_pages

from embedchain.helper_classes.json_serializable import register_deserializable
# from embedchain.loaders.base_loader import BaseLoader
from embedchain.utils import clean_string

from database.custom_embedchain.loaders.base_loader import BaseLoader

@register_deserializable
class PdfFileLoader(BaseLoader):
    def load_data(self, url):
        """Load data from a PDF file."""
        # loader = PyPDFLoader(url)
        # pages = loader.load_and_split()
        pages = extract_pages(url)
        images = convert_from_path(url)
        # 이미지 변환
        output = []
        # if not len(pages):
        #     raise ValueError("No data found")
        # assert len(pages) == len(images)
        for idx, (image, page) in enumerate(zip(images, pages)):
            # content = page.page_content
            # content = clean_string(content)
            # meta_data = page.metadata
            meta_data = {}
            meta_data["url"] = url
            meta_data["page"] = idx+1
            output.append(
                {
                    "content": page,
                    "meta_data": meta_data,
                    "image": image, # 각 페이지의 이미지
                }
            )
        return output