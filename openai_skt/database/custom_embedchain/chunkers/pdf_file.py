import copy
import hashlib
from typing import Optional

import numpy as np
import camelot
from pdfminer.layout import LTTextContainer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# from embedchain.chunkers.base_chunker import BaseChunker
from embedchain.config.AddConfig import ChunkerConfig
from embedchain.helper_classes.json_serializable import register_deserializable
import layoutparser as lp
import cv2

from database.custom_embedchain.chunkers.base_chunker import BaseChunker

# layout_parser_model = lp.Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config', 
#                                  extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
#                                  label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})

def pixel_to_point(val):
    return val * 72 / 200  # Convert pixel to point using 200 DPI

def adjust_y(y, height):
    return height - y  # Adjust Y-coordinate

def inside(center, box):
    cx, cy = center
    bx1, by1, bx2, by2 = box
    return bx1 <= cx <= bx2 and by1 <= cy <= by2
@register_deserializable
class PdfFileChunker(BaseChunker):
    """Chunker for PDF file."""

    def __init__(self, config: Optional[ChunkerConfig] = None):
        if config is None:
            config = ChunkerConfig(chunk_size=1000, chunk_overlap=0, length_function=len)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=config.length_function,
        )
        super().__init__(text_splitter)
        # self.layout_parser_model = layout_parser_model
        self.layout_parser_model = None

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
            text_layout = data["content"] # From pdf file
            image = data["image"] # 이미지 스크린샷

            meta_data = data["meta_data"]
            # add data type to meta data to allow query using data type
            # meta_data["data_type"] = self.data_type.value
            url = meta_data["url"]

            chunks, meta_datas = self.get_chunks(text_layout, image, meta_data)
            
            for chunk, meta_data in zip(chunks, meta_datas):
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

    def get_chunks(self, text_layout, image, meta_data):
        """
        Returns chunks using text splitter instance.

        Override in child class if custom logic.
        """
        chunks = []
        meta_datas = []
        # return self.text_splitter.split_text(content)
        ## TODO 여기 GPU 서버랑 API 통신으로 바꾸기
        image_layout_results = self.layout_parser_model.detect(image)
        for image_layout_result in image_layout_results: # title, figure, text, table, list
            pixel_bounding_box = image_layout_result.coordinates # Get the four corners pixel values of the box (x1, y1, x2, y2)
            x1, y1, x2, y2 = [pixel_to_point(pixel_value) for pixel_value in pixel_bounding_box]  # Convert pixel values to point
            pdf_height = text_layout.height
            bounding_box = (x1, adjust_y(y2, pdf_height), x2, adjust_y(y1, pdf_height)) # image layout bounding box (x1, y1, x2, y2)
            single_meta_data = copy.deepcopy(meta_data)
            if image_layout_result.type == 'Text':
                single_meta_data["source_type"] = 'text'
                
                # 여기서 pdf부분과 text를 일치시켜야함
                texts_inside = []

                for element in text_layout:
                    if isinstance(element, LTTextContainer):
                        e_x1, e_y1, e_x2, e_y2 = element.bbox
                        e_center = ((e_x1 + e_x2) / 2, (e_y1 + e_y2) / 2)
                        
                        if inside(e_center, bounding_box):
                            texts_inside.append((e_y2, e_x1, element.get_text()))  # Y, X, and text
                texts_inside.sort(key=lambda x: (-x[0], x[1]))

                description = ''
                for _, _, text in texts_inside:
                    description += text.replace('\n', '')
                chunks.append(description)
                single_meta_data["data"] = description
                meta_datas.append(single_meta_data)
            elif image_layout_result.type == 'Table':
                single_meta_data["source_type"] = 'table'
                x1, y1, x2, y2 = bounding_box
                tables = camelot.read_pdf(single_meta_data['url'], pages=str(single_meta_data['page']), table_areas=[f'{x1},{y2},{x2},{y1}'])
                if len(tables) == 0:
                    raise ValueError("No table found")
                crop_image = image_layout_result.crop_image(np.array(image)) # numpy array
                md_text = tables[0].df.to_markdown() # 여기서 table 이미지를 마크다운으로 변경
                description = '' # 캡션 + comment 추가
                data = md_text + description
                single_meta_data["data"] = data
                chunks.append(data)
                meta_datas.append(single_meta_data)                
            elif image_layout_result.type == 'Figure':
                single_meta_data["source_type"] = 'image'
                crop_image = image_layout_result.crop_image(np.array(image)) # numpy array                
                single_meta_data["data"] = str(crop_image)
                description = '이미지에유' # 캡션 + comment 추가
                # 여기서 이미지캡션과 연결하고, 없으면 걍 버리기
                chunks.append(description)
                meta_datas.append(single_meta_data)
        return chunks, meta_datas