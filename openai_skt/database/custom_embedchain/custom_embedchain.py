import time
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import logging
import threading

# from embedchain.chunkers.base_chunker import BaseChunker
# from embedchain.loaders.base_loader import BaseLoader
from embedchain.embedchain import EmbedChain
from embedchain.embedder.openai_embedder import OpenAiEmbedder
from embedchain.helper_classes.json_serializable import register_deserializable
from embedchain.llm.openai_llm import OpenAiLlm
from embedchain.vectordb.chroma_db import ChromaDB
from embedchain.config import (AddConfig, AppConfig, BaseEmbedderConfig, BaseLlmConfig,
                               ChromaDbConfig)
# from embedchain.data_formatter import DataFormatter
# from embedchain.models.data_type import DataType
from embedchain.utils import detect_datatype

from database.custom_embedchain.chunkers.base_chunker import BaseChunker
from database.custom_embedchain.loaders.base_loader import BaseLoader
from database.custom_embedchain.data_formatter import DataFormatter
from database.custom_embedchain.data_type import DataType
from database.custom_embedchain.utils import detect_datatype


class CustomEmbedChain(EmbedChain):
    def __init__(
            self,
            system_prompt: Optional[str] = None,):
        config=AppConfig()
        llm = OpenAiLlm(config=None)
        embedder = OpenAiEmbedder(config=BaseEmbedderConfig(model="text-embedding-ada-002"))
        database = ChromaDB(config=None)
        super().__init__(config=config, llm=llm, db=database, embedder=embedder, system_prompt=system_prompt)

    def add(
        self,
        source: Any,
        data_type: Optional[DataType] = None,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[AddConfig] = None,
        source_type=None
    ):
        """
        Adds the data from the given URL to the vector db.
        Loads the data, chunks it, create embedding for each chunk
        and then stores the embedding to vector database.

        :param source: The data to embed, can be a URL, local file or raw content, depending on the data type.
        :type source: Any
        :param data_type: Automatically detected, but can be forced with this argument. The type of the data to add,
        defaults to None
        :type data_type: Optional[DataType], optional
        :param metadata: Metadata associated with the data source., defaults to None
        :type metadata: Optional[Dict[str, Any]], optional
        :param config: The `AddConfig` instance to use as configuration options., defaults to None
        :type config: Optional[AddConfig], optional
        :raises ValueError: Invalid data type
        :return: source_id, a md5-hash of the source, in hexadecimal representation.
        :rtype: str
        """
        if config is None:
            config = AddConfig()
        try:
            DataType(source)
            logging.warning(
                f"""Starting from version v0.0.40, Embedchain can automatically detect the data type. So, in the `add` method, the argument order has changed. You no longer need to specify '{source}' for the `source` argument. So the code snippet will be `.add("{data_type}", "{source}")`"""  # noqa #E501
            )
            logging.warning(
                "Embedchain is swapping the arguments for you. This functionality might be deprecated in the future, so please adjust your code."  # noqa #E501
            )
            source, data_type = data_type, source
        except ValueError:
            pass
        if data_type:
            try:
                data_type = DataType(data_type)
            except ValueError:
                raise ValueError(
                    f"Invalid data_type: '{data_type}'.",
                    f"Please use one of the following: {[data_type.value for data_type in DataType]}",
                ) from None
        if not data_type:
            data_type = detect_datatype(source)
        # `source_id` is the hash of the source argument
        hash_object = hashlib.md5(str(source).encode("utf-8"))
        source_id = hash_object.hexdigest()
        data_formatter = DataFormatter(data_type, config)
        # self.user_asks.append([source, data_type.value, metadata])
        documents, _metadatas, _ids, new_chunks = self.load_and_embed(
            data_formatter.loader, data_formatter.chunker, source, metadata, source_id, source_type
        )
        if data_type in {DataType.DOCS_SITE}:
            self.is_docs_site_instance = True
        # Send anonymous telemetry
        # if self.config.collect_metrics:
        #     # it's quicker to check the variable twice than to count words when they won't be submitted.
        #     word_count = sum([len(document.split(" ")) for document in documents])

        #     extra_metadata = {"data_type": data_type.value, "word_count": word_count, "chunks_count": new_chunks}
        #     thread_telemetry = threading.Thread(target=self._send_telemetry_event, args=("add", extra_metadata))
        #     thread_telemetry.start()
        return source_id

    async def async_add(
        self,
        source: Any,
        data_type: Optional[DataType] = None,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[AddConfig] = None,
    ):
        """
        Adds the data from the given URL to the vector db.
        Loads the data, chunks it, create embedding for each chunk
        and then stores the embedding to vector database.

        :param source: The data to embed, can be a URL, local file or raw content, depending on the data type.
        :type source: Any
        :param data_type: Automatically detected, but can be forced with this argument. The type of the data to add,
        defaults to None
        :type data_type: Optional[DataType], optional
        :param metadata: Metadata associated with the data source., defaults to None
        :type metadata: Optional[Dict[str, Any]], optional
        :param config: The `AddConfig` instance to use as configuration options., defaults to None
        :type config: Optional[AddConfig], optional
        :raises ValueError: Invalid data type
        :return: source_id, a md5-hash of the source, in hexadecimal representation.
        :rtype: str
        """
        if config is None:
            config = AddConfig()

        try:
            DataType(source)
            logging.warning(
                f"""Starting from version v0.0.40, Embedchain can automatically detect the data type. So, in the `add` method, the argument order has changed. You no longer need to specify '{source}' for the `source` argument. So the code snippet will be `.add("{data_type}", "{source}")`"""  # noqa #E501
            )
            logging.warning(
                "Embedchain is swapping the arguments for you. This functionality might be deprecated in the future, so please adjust your code."  # noqa #E501
            )
            source, data_type = data_type, source
        except ValueError:
            pass

        if data_type:
            try:
                data_type = DataType(data_type)
            except ValueError:
                raise ValueError(
                    f"Invalid data_type: '{data_type}'.",
                    f"Please use one of the following: {[data_type.value for data_type in DataType]}",
                ) from None
        if not data_type:
            data_type = detect_datatype(source)
        # `source_id` is the hash of the source argument
        hash_object = hashlib.md5(str(source).encode("utf-8"))
        source_id = hash_object.hexdigest()

        data_formatter = DataFormatter(data_type, config)
        self.user_asks.append([source, data_type.value, metadata])
        documents, _metadatas, _ids, new_chunks = await self.async_load_and_embed(
            data_formatter.loader, data_formatter.chunker, source, metadata, source_id
        )
        if data_type in {DataType.DOCS_SITE}:
            self.is_docs_site_instance = True

        # Send anonymous telemetry
        if self.config.collect_metrics:
            # it's quicker to check the variable twice than to count words when they won't be submitted.
            word_count = sum([len(document.split(" ")) for document in documents])

            extra_metadata = {"data_type": data_type.value, "word_count": word_count, "chunks_count": new_chunks}
            thread_telemetry = threading.Thread(target=self._send_telemetry_event, args=("add", extra_metadata))
            thread_telemetry.start()

        return source_id
    
    async def async_load_and_embed(
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
            # print(f"All data from {src} already exists in the database.")
            # Make sure to return a matching return type
            return [], [], [], 0

        embeddings_data = await chunker.async_create_chunks(loader, src) # 병목

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
                # print(f"All data from {src} already exists in the database.")
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

        self.db.add(documents=documents, metadatas=metadatas, ids=ids) # 병목
        count_new_chunks = self.db.count() - chunks_before_addition
        # print((f"Successfully saved {src} ({chunker.data_type}). New chunks count: {count_new_chunks}"))
        return list(documents), metadatas, ids, count_new_chunks

    def load_and_embed(
        self,
        loader: BaseLoader,
        chunker: BaseChunker,
        src: Any,
        metadata: Optional[Dict[str, Any]] = None,
        source_id: Optional[str] = None,
        source_type=None
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
            # print(f"All data from {src} already exists in the database.")
            # Make sure to return a matching return type
            return [], [], [], 0
        embeddings_data = chunker.create_chunks(loader, src) # 병목
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
                # print(f"All data from {src} already exists in the database.")
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
            if source_type is not None:
                m["data_source_type"] = source_type
            # m["data_source_type"] = "koreakr"

            # Note: Metadata is the function argument
            if metadata:
                # Spread whatever is in metadata into the new object.
                m.update(metadata)

            new_metadatas.append(m)
        metadatas = new_metadatas
        # Count before, to calculate a delta in the end.
        chunks_before_addition = self.db.count()
        try:
            self.db.add(documents=documents, metadatas=metadatas, ids=ids) # 병목
        except:
            return [], [], [], 0
        count_new_chunks = self.db.count() - chunks_before_addition
        # print((f"Successfully saved {src} ({chunker.data_type}). New chunks count: {count_new_chunks}"))
        return list(documents), metadatas, ids, count_new_chunks