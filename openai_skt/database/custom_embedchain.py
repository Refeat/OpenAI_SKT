from typing import Any, Dict, List, Optional, Tuple

from embedchain.chunkers.base_chunker import BaseChunker
from embedchain.config.apps.BaseAppConfig import BaseAppConfig
from embedchain.loaders.base_loader import BaseLoader
from embedchain.embedchain import EmbedChain
from embedchain.embedder.openai_embedder import OpenAiEmbedder
from embedchain.helper_classes.json_serializable import register_deserializable
from embedchain.llm.openai_llm import OpenAiLlm
from embedchain.vectordb.chroma_db import ChromaDB
from embedchain.config import (AppConfig, BaseEmbedderConfig, BaseLlmConfig,
                               ChromaDbConfig)

class CustomEmbedChain(EmbedChain):
    def __init__(
            self,
            system_prompt: Optional[str] = None,):
        config=AppConfig()
        llm = OpenAiLlm(config=None)
        embedder = OpenAiEmbedder(config=BaseEmbedderConfig(model="text-embedding-ada-002"))
        database = ChromaDB(config=None)
        super().__init__(config=config, llm=llm, db=database, embedder=embedder, system_prompt=system_prompt)

    def load_and_embed(
        self,
        loader: BaseLoader,
        chunker: BaseChunker,
        src: Any,
        metadata: Optional[Dict[str, Any]] = None,
        source_id: Optional[str] = None,
    ) -> Tuple[List[str], Dict[str, Any], List[str], int]:
        """The loader to use to load the data.

        :param loader: The loader to use to load the data.
        :type loader: BaseLoader
        :param chunker: The chunker to use to chunk the data.
        :type chunker: BaseChunker
        :param src: The data to be handled by the loader.
        Can be a URL for remote sources or local content for local loaders.
        :type src: Any
        :param metadata: Metadata associated with the data source., defaults to None
        :type metadata: Dict[str, Any], optional
        :param source_id: Hexadecimal hash of the source., defaults to None
        :type source_id: str, optional
        :return: (List) documents (embedded text), (List) metadata, (list) ids, (int) number of chunks
        :rtype: Tuple[List[str], Dict[str, Any], List[str], int]
        """
        # get existing ids, and discard doc if any common id exist.
        where = {"app_id": self.config.id} if self.config.id is not None else {}
        # where={"url": src}
        source_id_in_db = self.db.get(
            ids=[],
            where={'hash':source_id},  # optional filter
        )
        if len(source_id_in_db):
            print(f"All data from {src} already exists in the database.")
            # Make sure to return a matching return type
            return [], [], [], 0

        embeddings_data = chunker.create_chunks(loader, src)

        # spread chunking results
        documents = embeddings_data["documents"]
        metadatas = embeddings_data["metadatas"]
        ids = embeddings_data["ids"]

        # get existing ids, and discard doc if any common id exist.
        # where = {"app_id": self.config.id} if self.config.id is not None else {}
        # where={"url": src}
        existing_ids = self.db.get(
            ids=ids,
            where=where,  # optional filter
        )

        if len(existing_ids):
            data_dict = {id: (doc, meta) for id, doc, meta in zip(ids, documents, metadatas)}
            data_dict = {id: value for id, value in data_dict.items() if id not in existing_ids}

            if not data_dict:
                print(f"All data from {src} already exists in the database.")
                # Make sure to return a matching return type
                return [], [], [], 0

            ids = list(data_dict.keys())
            documents, metadatas = zip(*data_dict.values())

        # Loop though all metadatas and add extras.
        new_metadatas = []
        for m in metadatas:
            # Add app id in metadatas so that they can be queried on later
            if self.config.id:
                m["app_id"] = self.config.id

            # Add hashed source
            m["hash"] = source_id

            # Note: Metadata is the function argument
            if metadata:
                # Spread whatever is in metadata into the new object.
                m.update(metadata)

            new_metadatas.append(m)
        metadatas = new_metadatas

        # Count before, to calculate a delta in the end.
        chunks_before_addition = self.db.count()

        self.db.add(documents=documents, metadatas=metadatas, ids=ids)
        count_new_chunks = self.db.count() - chunks_before_addition
        print((f"Successfully saved {src} ({chunker.data_type}). New chunks count: {count_new_chunks}"))
        return list(documents), metadatas, ids, count_new_chunks