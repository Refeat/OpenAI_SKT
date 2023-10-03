import os
import re
import copy
import time
import hashlib
from typing import Optional
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import camelot
from pdfminer.layout import LTTextContainer
from langchain.text_splitter import RecursiveCharacterTextSplitter

from embedchain.config.AddConfig import ChunkerConfig
from embedchain.helper_classes.json_serializable import register_deserializable

from database.custom_embedchain.chunkers.base_chunker import BaseChunker
from api import ClovaOCRAPI

def inside(center, box):
    cx, cy = center
    bx1, by1, bx2, by2 = box
    return bx1 <= cx <= bx2 and by1 <= cy <= by2

clova_ocr_api = ClovaOCRAPI()

@register_deserializable
class JsonFileChunker(BaseChunker):
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
            image_layout = data["image"] # from layout parser
            
            meta_data = data["meta_data"]
            
            url = meta_data["url"]
            chunks, meta_datas = self.get_chunks(text_layout, image_layout, meta_data)
            
            for chunk, meta_data in zip(chunks, meta_datas):
                if meta_data['source_type'] == 'table':
                    print(chunk, meta_data['data'])
                elif meta_data['source_type'] == 'image':
                    print(chunk, meta_data['data'])
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

    def pixel_to_point_bounding_box(self, pdf_height, pixel_bounding_box):
        def pixel_to_point(val):
            return val * 72 / 200  # Convert pixel to point using 200 DPI

        def adjust_y(y, height):
            return height - y  # Adjust Y-coordinate
        
        x1, y1, x2, y2 = [pixel_to_point(pixel_value) for pixel_value in pixel_bounding_box]  # Convert pixel values to point
        point_bounding_box = (x1, adjust_y(y2, pdf_height), x2, adjust_y(y1, pdf_height)) # image layout bounding box (x1, y1, x2, y2)
        return point_bounding_box

    def get_chunks(self, text_layout, image_layout, meta_data):
        """
        Returns chunks using text splitter instance.

        Override in child class if custom logic.
        """
        chunks = []
        meta_datas = []
        image_layout_results = image_layout

        pdf_height = text_layout.height
        
        for image_layout_result in image_layout_results: # title, figure, text, table, list
            main_bbox = image_layout_result['main_bbox'] # Get the four corners pixel values of the box (x1, y1, x2, y2)
            pixel_bounding_box = [main_bbox['x_1'], main_bbox['y_1'], main_bbox['x_2'], main_bbox['y_2']]
            bounding_box = self.pixel_to_point_bounding_box(pdf_height, pixel_bounding_box)  # Convert pixel values to point
            
            single_meta_data = copy.deepcopy(meta_data)
            if image_layout_result['source_type'] == 'contents':
                single_meta_data["source_type"] = 'text'
                
                texts_inside = []
                for element in text_layout:
                    if isinstance(element, LTTextContainer):
                        e_x1, e_y1, e_x2, e_y2 = element.bbox
                        e_center = ((e_x1 + e_x2) / 2, (e_y1 + e_y2) / 2)
                        
                        if inside(e_center, bounding_box):
                            texts_inside.append((e_y2, e_x1, element.get_text()))  # Y, X, and text

                if len(texts_inside) == 0:
                    continue
                texts_inside.sort(key=lambda x: (-x[0], x[1]))

                description = ''
                for _, _, text in texts_inside:
                    description += text.replace('\n', '')
                description = re.sub(' +', ' ', description)                
                
                for chunk in self.text_splitter.split_text(description):
                    chunks.append(chunk)
                    single_meta_data["data"] = chunk
                    meta_datas.append(single_meta_data)
            elif image_layout_result['source_type'] == 'table':
                single_meta_data["source_type"] = 'table'
                x1, y1, x2, y2 = bounding_box
                # tables = camelot.read_pdf(single_meta_data['path'], pages=str(single_meta_data['page']), table_areas=[f'{x1},{y2},{x2},{y1}'])
                tables = camelot.layout_pdf(imagepath=single_meta_data["image_path"], layout=text_layout, table_areas=[f'{x1},{y2},{x2},{y1}'])
                if len(tables) == 0:
                    # print('No table found')
                    continue
                
                try:
                    md_text = tables[0].df.to_markdown()
                except:
                    print('error on markdown')
                    continue
                
                # Extract comments and caption
                comments = []
                captions = []
                comment_boxes = image_layout_result.get('comments', [])
                caption_box = image_layout_result.get('caption', None)
                if len(comment_boxes) == 0 and caption_box is None:
                    continue
                for comment_box in comment_boxes:
                    comment_bbox = comment_box['comment_bbox']
                    comment_pixel_bounding_box = [comment_bbox['x_1'], comment_bbox['y_1'], comment_bbox['x_2'], comment_bbox['y_2']]
                    comment_bounding_box = self.pixel_to_point_bounding_box(pdf_height, comment_pixel_bounding_box)  # Convert pixel values to point

                    
                    comment_texts = []
                    
                    for element in text_layout:
                        if isinstance(element, LTTextContainer):
                            e_x1, e_y1, e_x2, e_y2 = element.bbox
                            e_center = ((e_x1 + e_x2) / 2, (e_y1 + e_y2) / 2)
                            
                            if inside(e_center, comment_bounding_box):
                                comment_texts.append(element.get_text())
                    
                    comments.append(' '.join(comment_texts))

                
                if caption_box:
                    caption_texts = []
                    caption_bbox = caption_box['caption_bbox']
                    caption_pixel_bounding_box = [caption_bbox['x_1'], caption_bbox['y_1'], caption_bbox['x_2'], caption_bbox['y_2']]
                    caption_bounding_box = self.pixel_to_point_bounding_box(pdf_height, caption_pixel_bounding_box)  # Convert pixel values to point
                    
                    for element in text_layout:
                        if isinstance(element, LTTextContainer):
                            e_x1, e_y1, e_x2, e_y2 = element.bbox
                            e_center = ((e_x1 + e_x2) / 2, (e_y1 + e_y2) / 2)
                            
                            if inside(e_center, caption_bounding_box):
                                caption_texts.append(element.get_text())
                    
                    captions.append(' '.join(caption_texts))
                
                description = ''
                
                if len(captions) != 0:
                    description += f'Caption: {" ".join(captions)}\n'
                if len(comments) != 0:
                    description += f'Comments: {" ".join(comments)}\n'

                data = description + '\n' + md_text
                single_meta_data["data"] = data
                chunks.append(description)
                meta_datas.append(single_meta_data)
            elif image_layout_result['source_type'] == 'figure' or image_layout_result['source_type'] == 'graph':
                single_meta_data["source_type"] = 'image'
                crop_image = Image.open(image_layout_result['crop_image_path'])
                
                

                single_meta_data["data"] = image_layout_result['crop_image_path']
                
                # Extract caption
                caption_box = image_layout_result.get('caption', None)
                captions = []
                if caption_box:
                    caption_bbox = caption_box['caption_bbox']
                    caption_pixel_bounding_box = [caption_bbox['x_1'], caption_bbox['y_1'], caption_bbox['x_2'], caption_bbox['y_2']]
                    caption_bounding_box = self.pixel_to_point_bounding_box(pdf_height, caption_pixel_bounding_box)  # Convert pixel values to point
                    caption_texts = []
                    
                    for element in text_layout:
                        if isinstance(element, LTTextContainer):
                            e_x1, e_y1, e_x2, e_y2 = element.bbox
                            e_center = ((e_x1 + e_x2) / 2, (e_y1 + e_y2) / 2)
                            
                            if inside(e_center, caption_bounding_box):
                                caption_texts.append(element.get_text())
                    
                    captions.append(' '.join(caption_texts))

                caption_text = ''
                if len(captions) == 0:
                    continue
                else:
                    caption_text = f'Caption: {" ".join(captions)}'    
                    
                if image_layout_result['source_type'] == 'figure':
                    contents = clova_ocr_api.get_text(np.array(crop_image))
                    for content in self.text_splitter.split_text(contents):
                        chunk = caption_text + '\n' + content
                        chunks.append(chunk)
                        meta_datas.append(single_meta_data)
                else:
                    chunk = caption_text
                    chunks.append(chunk)
                    meta_datas.append(single_meta_data)
        
        return chunks, meta_datas