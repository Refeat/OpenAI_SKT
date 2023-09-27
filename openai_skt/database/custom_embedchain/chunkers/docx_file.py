from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter

# from embedchain.chunkers.base_chunker import BaseChunker
from embedchain.config.AddConfig import ChunkerConfig
from embedchain.helper_classes.json_serializable import register_deserializable

from database.custom_embedchain.chunkers.base_chunker import BaseChunker

@register_deserializable
class DocxFileChunker(BaseChunker):
    """Chunker for PDF file."""

    def __init__(self, config: Optional[ChunkerConfig] = None, layout_parser_model=None):
        if config is None:
            config = ChunkerConfig(chunk_size=1000, chunk_overlap=0, length_function=len)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=config.length_function,
        )
        super().__init__(text_splitter)
        self.layout_parser_model = layout_parser_model

    def create_chunks(self, loader, src):
        """
        Loads data and chunks it.

        :param loader: The loader which's `load_data` method is used to create
        the raw data.
        :param src: The data to be handled by the loader. Can be a URL for
        remote sources or local content for local loaders.
        """
        documents = []
        ids = []
        idMap = {}
        datas = loader.load_data(src)
        metadatas = []
        for data in datas:
            content = data["content"]
            image = data["image"]

            meta_data = data["meta_data"]
            # add data type to meta data to allow query using data type
            meta_data["data_type"] = self.data_type.value
            url = meta_data["url"]

            chunks = self.get_chunks(content)
            
            for chunk in chunks:
                chunk_id = hashlib.sha256((chunk + url).encode()).hexdigest()
                if idMap.get(chunk_id) is None:
                    idMap[chunk_id] = True
                    ids.append(chunk_id)
                    documents.append(chunk)
                    metadatas.append(meta_data)
        return {
            "documents": documents,
            "ids": ids,
            "metadatas": metadatas,
        }

    def get_chunks(self, content):
        """
        Returns chunks using text splitter instance.

        Override in child class if custom logic.
        """
        # return self.text_splitter.split_text(content)
        layout_results = self.layout_parser_model.detect(image)
        for layout_result in layout_results: # title, figure, text, table, list
            if layout_result.type == 'text':
                # 여기서 pdf부분과 text를 일치시켜야함
                pass
            elif layout_result.type == 'table':
                layout_result.crop_image(image) # output shape: (height, width, color)
                # 여기서 table 이미지를 마크다운으로 변경
            elif layout_result.type == 'figure':
                layout_result.crop_image(image)