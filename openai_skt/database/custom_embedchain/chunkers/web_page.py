import hashlib

from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter

# from embedchain.chunkers.base_chunker import BaseChunker
from embedchain.config.AddConfig import ChunkerConfig
from embedchain.helper_classes.json_serializable import register_deserializable

from database.custom_embedchain.chunkers.base_chunker import BaseChunker

@register_deserializable
class WebPageChunker(BaseChunker):
    """Chunker for web page."""

    def __init__(self, config: Optional[ChunkerConfig] = None):
        if config is None:
            config = ChunkerConfig(chunk_size=500, chunk_overlap=0, length_function=len)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=config.length_function,
        )
        super().__init__(text_splitter)


def group_based_create_chunks(self, loader, src):
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
        data_result = loader.load_data(src)
        data_records = data_result["data"]
        doc_id = data_result["doc_id"]

        metadatas = []
        for data in data_records:
            content = data["content"]

            meta_data = data["meta_data"]
            # add data type to meta data to allow query using data type
            meta_data["data_type"] = self.data_type.value
            meta_data["doc_id"] = doc_id
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
            "doc_id": doc_id,
        }

def group_based_get_chunks(self, content):
    chunks = []
    for strings in content:
        chunks.extend(self.text_splitter.split_text(strings))
    
    return chunks

# WebPageChunker.create_chunks = group_based_create_chunks
# WebPageChunker.get_chunks = group_based_get_chunks

# WebPageChunker.create_chunks = group_based_create_chunks

