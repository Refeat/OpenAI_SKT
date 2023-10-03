import os
import json
from typing import List

import layoutparser as lp
from pdf2image import convert_from_path
from PIL import Image
import numpy as np

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
parent_directory = os.path.dirname(current_directory)
grandparent_directory = os.path.dirname(parent_directory)
config_path = os.path.join(parent_directory, "chunk", "layout-parser-checkpoint", "config.yaml")
model_path = os.path.join(parent_directory, "chunk", "layout-parser-checkpoint", "model_final.pth")

from json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, lp.Rectangle): 
            return {
                "x_1": obj.x_1,
                "y_1": obj.y_1,
                "x_2": obj.x_2,
                "y_2": obj.y_2
            }
        return super().default(obj)


class LayoutModel:
    def __init__(self):
        self.model = lp.models.Detectron2LayoutModel(
            config_path=config_path,
            model_path=model_path,
            label_map={0: "topic", 1: "title", 2: "contents", 3: "figure",
                       4: "graph", 5: "table", 6: "table_caption", 7: "comment"},
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
        )
        self.domain = None

    def load_image(self, image_path):
        image = Image.open(image_path)
        return np.array(image)

    def detect_layout(self, image_array):
        self.image = image_array
        return self.model.detect(image_array)

    def set_domain(self, domain):
        self.domain = domain
        self.save_json_root_path = os.path.join(grandparent_directory, "data", self.domain, "json")
        self.save_image_root_path = os.path.join(grandparent_directory, "data", self.domain, "image")
        os.makedirs(self.save_json_root_path, exist_ok=True)
        os.makedirs(self.save_image_root_path, exist_ok=True)

    def post_process(self, layout):
        topic_blocks = lp.Layout([b for b in layout if b.type == "topic"])
        title_blocks = lp.Layout([b for b in layout if b.type == "title"])
        text_blocks = lp.Layout([b for b in layout if b.type == "contents"])
        figure_blocks = lp.Layout([b for b in layout if b.type == "figure"])
        graph_blocks = lp.Layout([b for b in layout if b.type == "graph"])
        table_blocks = lp.Layout([b for b in layout if b.type == "table"])
        table_caption_blocks = lp.Layout([b for b in layout if b.type == "table_caption"])
        comment_blocks = lp.Layout([b for b in layout if b.type == "comment"])

        text_blocks = lp.Layout([b for b in text_blocks if not any(b.is_in(b_fig) for b_fig in figure_blocks)])

        results = self.match_comments(text_blocks, figure_blocks, graph_blocks, table_blocks, table_caption_blocks, comment_blocks)

        return results

    def match_comments(self, text_blocks, figure_blocks, graph_blocks, table_blocks, table_caption_blocks, comment_blocks):
        '''
        outpout type : list of dictionary
        type : String => table, graph, figure
        main_bbox : Rectangle => 각 type의 메인 bbox (comments나 caption이 아님, 즉 표나 그래프나 사진의 bbox)
        comments : list of Rectangle  => 한 figure안에 여러 comments가 있을 수도 있음
        caption : Rectangle => type이 table인 경우만 있음
        '''
        output =[]
        # match talbe - comments - caption
        for text_block in text_blocks:
            output.append({"main_bbox" : text_block.block, "source_type" : "contents"})
        for table_block in table_blocks:
            comments_near_table = []
            for comment_block in comment_blocks:
                comment_y_center = (comment_block.block.y_1 + comment_block.block.y_2) / 2
                comment_x_center = (comment_block.block.x_1 + comment_block.block.x_2) / 2
                if (abs(comment_y_center - table_block.block.y_1 ) <= 80  or abs(comment_y_center - table_block.block.y_2) <= 80) and (comment_x_center < table_block.block.x_2  and comment_x_center > table_block.block.x_1):
                    comments_near_table.append(comment_block.block)
            table_caption = None
            y_value_constraints = 150
            for table_caption_block in table_caption_blocks:
                table_caption_x_center = (table_caption_block.block.x_1 + table_caption_block.block.x_2) /2
                table_caption_y_center = (table_caption_block.block.y_1 + table_caption_block.block.y_2) /2
                y1_near = abs(table_caption_y_center - table_block.block.y_1 )
                y2_near = abs(table_caption_y_center - table_block.block.y_2)
                if ( y1_near <= y_value_constraints  or y2_near <= y_value_constraints) and ( table_caption_x_center < table_block.block.x_2  and table_caption_x_center > table_block.block.x_1):
                    y_value_constraints = min(y1_near,y2_near)
                    table_caption = table_caption_block.block
            output.append({"main_bbox" : table_block.block, "comments" : comments_near_table, "caption" : table_caption, "source_type" : "table" })
        # match graph - comments
        for  graph_block in graph_blocks:
            comments_near_graph = []
            for comment_block in comment_blocks:
                comment_y_center = (comment_block.block.y_1 + comment_block.block.y_2) / 2
                comment_x_center = (comment_block.block.x_1 + comment_block.block.x_2) / 2
                if (abs(comment_y_center - graph_block.block.y_1 ) <= 80  or abs(comment_y_center - graph_block.block.y_2) <= 80) and (comment_x_center > graph_block.block.x_1 and comment_x_center < graph_block.block.x_2 ) : 
                    comments_near_graph.append(comment_block.block)
            
            output.append({"main_bbox" : graph_block.block, "comments" : comments_near_graph, "source_type" : "graph"})

        # match figure - comments
        for figure_block in figure_blocks:
            comments_near_figure = []
            for comment_block in comment_blocks:
                comment_y_center = (comment_block.block.y_1 + comment_block.block.y_2) / 2
                comment_x_center = (comment_block.block.x_1 + comment_block.block.x_2) / 2
                if (abs(comment_y_center - figure_block.block.y_1 ) <= 80  or abs(comment_y_center - figure_block.block.y_2) <= 80) and (comment_x_center >figure_block.block.x_1 and comment_x_center < figure_block.block.x_2 ) : 
                    comments_near_figure.append(comment_block.block)
            
            output.append({"main_bbox" : figure_block.block, "comments" : comments_near_figure, "source_type" : "figure"})

        return output

    def save_image(self, image:Image, image_path:str):
        image.save(image_path)

    def crop_image(self, image:Image, bbox:lp.Rectangle):
        if not bbox:
            print("Warning: bbox is an empty list. Skipping crop.")
            return None  # 또는 다른 적절한 기본값/처리
        return image.crop((bbox.x_1, bbox.y_1, bbox.x_2, bbox.y_2))

    def __call__(self, data_path:str):
        if self.domain is None:
            raise ValueError("domain is not set. Please use set_domain method.")
        if data_path.endswith('pdf'):
            image_list = []
            images = convert_from_path(data_path)
            base_path = os.path.basename(data_path)
            image_root_path = os.path.join(self.save_image_root_path, base_path)
            os.makedirs(image_root_path, exist_ok=True)
            for idx, image in enumerate(images):
                image_path = os.path.join(image_root_path, (f"{str(idx)}" + ".png"))
                self.save_image(image, image_path)
                image_list.append((image_path, image))
        else:
            raise ValueError("data_path must be a pdf file.")
        
        json_results = {}
        json_results["url"] = data_path
        json_results["name"] = os.path.basename(data_path)
        json_results["content"] = []

        for (image_path, image) in image_list:
            image_array = np.array(image)
            layout = self.detect_layout(image_array)
            results = self.post_process(layout)
            content_list = []
            
            for idx, result in enumerate(results):
                result["image_path"] = image_path
                
                # Main block image crop and save
                crop_image = self.crop_image(image, result["main_bbox"])
                crop_image_path = image_path.replace(".png", f"_{str(idx)}" + f"_{result['source_type']}" + ".png")
                self.save_image(crop_image, crop_image_path)
                result["crop_image_path"] = crop_image_path

                # Check the source type and update json_results accordingly
                if result["source_type"] in ["table", "graph", "figure"]:
                    if "comments" not in result:
                        result["comments"] = []
                        
                    # Crop and save each comment image
                    if len(result["comments"]) != 0:                        
                        comment_list = []
                        for comment_idx, comment in enumerate(result["comments"]):
                            comment_dict = {}
                            comment_crop_image = self.crop_image(image, comment)
                            comment_crop_image_path = image_path.replace(".png", f"_{str(idx)}_{str(comment_idx)}_comment.png")
                            self.save_image(comment_crop_image, comment_crop_image_path)
                            comment_dict['crop_image_path'] = comment_crop_image_path
                            comment_dict['comment_bbox'] = comment
                            comment_list.append(comment_dict)
                        result["comments"] = comment_list
                        
                    if "caption" not in result:
                        result["caption"] = None
                        
                    # Crop and save caption image for tables
                    if "caption_image_path" not in result and result["source_type"] == "table":
                        if result["caption"] is not None:
                            caption_dict = {}
                            caption_crop_image = self.crop_image(image, result["caption"])
                            caption_crop_image_path = image_path.replace(".png", f"_{str(idx)}_caption.png")
                            self.save_image(caption_crop_image, caption_crop_image_path)
                            caption_dict['crop_image_path'] = caption_crop_image_path
                            caption_dict['caption_bbox'] = result["caption"]
                            result["caption"] = caption_dict
                content_list.append(result)
            json_results["content"].append(content_list)

        json_path = os.path.join(self.save_json_root_path, base_path).replace(".pdf", ".json")
        self.save_json(json_results, json_path)
        return json_results['content']

    def save_json(self, results, json_path):
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4, cls=CustomJSONEncoder)



# Usage example
if __name__ == "__main__":
    layout_model = LayoutModel()
    layout_model.set_domain("kostat")
    
    image_path = "/root/OpenAI_SKT/openai_skt/database/chunk/layout-parser-checkpoint/(12조간)자동차과, 2022년 10월 자동차산업 동향(잠정).pdf"
    layout_model(image_path)

    # print(results)
