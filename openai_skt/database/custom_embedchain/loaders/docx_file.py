from langchain.document_loaders import Docx2txtLoader
from pdf2image import convert_from_path

from embedchain.helper_classes.json_serializable import register_deserializable
from embedchain.loaders.base_loader import BaseLoader
from embedchain.utils import clean_string

@register_deserializable
class DocxFileLoader(BaseLoader):
    def load_data(self, url):
        """Load data from a PDF file."""
        loader = Docx2txtLoader(url)
        # images = convert_from_path(url)
        # 이미지 변환
        output = []
        data = loader.load()
        content = data[0].page_content
        meta_data = data[0].metadata
        meta_data["url"] = "local"
        output.append({"content": content, "meta_data": meta_data})
        return output