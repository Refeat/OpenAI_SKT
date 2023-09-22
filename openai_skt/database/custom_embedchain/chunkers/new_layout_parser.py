import os
import matplotlib.pyplot as plt
import time
from pycocotools.coco import COCO
import layoutparser as lp
import random
import cv2
from PIL import Image
import torchvision.transforms as transforms
import torch
import numpy as np

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
parent_directory = os.path.dirname(current_directory)
grandparent_directory = os.path.dirname(parent_directory)
config_path = os.path.join(grandparent_directory, "chunk", "layout-parser-checkpoint", "config.yaml")
model_path = os.path.join(grandparent_directory, "chunk", "layout-parser-checkpoint", "model_final.pth")

class LayoutModel:
    def __init__(self):
        self.model = lp.models.Detectron2LayoutModel(
            config_path=config_path,
            model_path=model_path,
            label_map={0: "topic", 1: "title", 2: "contents", 3: "figure",
                       4: "graph", 5: "table", 6: "table_caption", 7: "comment"},
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
        )

    def load_image(self, image_path):
        image = Image.open(image_path)
        return np.array(image)

    def detect_layout(self, image_array):
        self.image = image_array
        return self.model.detect(image_array)

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
            output.append({"main_bbox" : text_block.block, "type" : "contents" })
        for table_block in table_blocks:
            comments_near_table = []
            for comment_block in comment_blocks:
                comment_y_center = (comment_block.block.y_1 + comment_block.block.y_2) / 2
                comment_x_center = (comment_block.block.x_1 + comment_block.block.x_2) / 2
                if (abs(comment_y_center - table_block.block.y_1 ) <= 80  or abs(comment_y_center - table_block.block.y_2) <= 80) and (comment_x_center < table_block.block.x_2  and comment_x_center > table_block.block.x_1):
                    comments_near_table.append(comment_block.block)
            table_caption = []
            y_value_constraints = 150
            for table_caption_block in table_caption_blocks:
                table_caption_x_center = (table_caption_block.block.x_1 + table_caption_block.block.x_2) /2
                table_caption_y_center = (table_caption_block.block.y_1 + table_caption_block.block.y_2) /2
                y1_near = abs(table_caption_y_center - table_block.block.y_1 )
                y2_near = abs(table_caption_y_center - table_block.block.y_2)
                if ( y1_near <= y_value_constraints  or y2_near <= y_value_constraints) and ( table_caption_x_center < table_block.block.x_2  and table_caption_x_center > table_block.block.x_1):
                    y_value_constraints = min(y1_near,y2_near)
                    table_caption = table_caption_block.block
            output.append({"main_bbox" : table_block.block, "comments" : comments_near_table, "caption" : table_caption, "type" : "table" })
        # match graph - comments
        for  graph_block in graph_blocks:
            comments_near_graph = []
            for comment_block in comment_blocks:
                comment_y_center = (comment_block.block.y_1 + comment_block.block.y_2) / 2
                comment_x_center = (comment_block.block.x_1 + comment_block.block.x_2) / 2
                if (abs(comment_y_center - graph_block.block.y_1 ) <= 80  or abs(comment_y_center - graph_block.block.y_2) <= 80) and (comment_x_center > graph_block.block.x_1 and comment_x_center < graph_block.block.x_2 ) : 
                    comments_near_graph.append(comment_block.block)
            
            output.append({"main_bbox" : graph_block.block, "comments" : comments_near_graph, "type" : "graph"})

        # match figure - comments
        for figure_block in figure_blocks:
            comments_near_figure = []
            for comment_block in comment_blocks:
                comment_y_center = (comment_block.block.y_1 + comment_block.block.y_2) / 2
                comment_x_center = (comment_block.block.x_1 + comment_block.block.x_2) / 2
                if (abs(comment_y_center - figure_block.block.y_1 ) <= 80  or abs(comment_y_center - figure_block.block.y_2) <= 80) and (comment_x_center >figure_block.block.x_1 and comment_x_center < figure_block.block.x_2 ) : 
                    comments_near_figure.append(comment_block.block)
            
            output.append({"main_bbox" : figure_block.block, "comments" : comments_near_figure, "type" : "figure"})

        return output

    def __call__(self, image_path=None, image_array=None):
        if image_path is not None:
            image_array = self.load_image(image_path)
        layout = self.detect_layout(image_array)
        results = self.post_process(layout)
        return results

# Usage example
if __name__ == "__main__":
    layout_model = LayoutModel()
    # image_path = ""
    # results = layout_model(image_path)

    # print(results)
