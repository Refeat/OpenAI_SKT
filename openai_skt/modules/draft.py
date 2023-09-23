import os
import json
from typing import Any

from database import Chunk

import json

class Draft:
    def __init__(self, draft_id=None, purpose=None, tables=None, text=None) -> None:
        self.draft_id = draft_id
        if text is None:
            self.text = f'# {purpose}\n'
        else:
            self.text = text
        self.purpose = purpose
        self.tables = tables
        self.files = set()  # initialize as set
        self.draft_parts = list()

    def edit(self, draft_part, modified_draft_part):
        # 일단 전체 드래프트만 바꿈. 나중에 각 draft_part의 text도 바꿔야 함
        self.text = self.text.replace(draft_part, modified_draft_part)
        # TODO: 각 draft_part의 text도 바꾸기. 근데 어떻게 자를지 애매한 부분이 있음
        pass


    def add_draft_part(self, draft_part):
        if self.text is None:
            self.text = f'{self.purpose}\n'
        self.text += draft_part.text + '\n'
        self.files.update(draft_part.files)  # use update method for sets
        self.draft_parts.append(draft_part)

    def __str__(self) -> str:
        return self.text

    def to_dict(self):
        return {
            'draft_id': self.draft_id,
            'text': self.text,
            'purpose': self.purpose,
            'tables': self.tables,
            'draft_parts': [draft_part.to_dict() for draft_part in self.draft_parts] if self.draft_parts else []
        }

    @classmethod
    def load(cls, draft_path): # draft_path: json file path
        with open(draft_path, 'r', encoding='utf-8') as f:
            draft_dict = json.load(f)
        draft_id = draft_dict['draft_id']
        text = draft_dict['text']
        purpose = draft_dict['purpose']
        tables = draft_dict['tables']
        draft = cls(draft_id=draft_id, purpose=purpose, tables=tables, text=text)
        draft.draft_parts = [DraftPart.load(draft_part) for draft_part in draft_dict['draft_parts']]
        for draft_part in draft.draft_parts:
            draft.files.update(draft_part.files)  # use update method for sets
        return draft

    def save(self, draft_json_path=None, draft_root_path=None):
        if draft_json_path is not None:
            json_path = draft_json_path
            md_path = draft_json_path.replace('.json', '.md')
        elif draft_root_path is not None:
            os.makedirs(draft_root_path, exist_ok=True)
            json_path = os.path.join(draft_root_path, f"draft_{self.draft_id}.json")
            md_path = os.path.join(draft_root_path, f"draft_{self.draft_id}.md")
        else:
            raise Exception("Either draft_json_path or draft_root_path must be specified")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
        print(f"saved draft to {json_path}")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self.text)
        print(f"saved draft to {md_path}")

class DraftPart:
    def __init__(self, text=None, single_table=None, files=None):
        self.text = text
        self.single_table = single_table
        self.files = set(files) # [chunk1, chunk2, chunk3]

    def edit(self):
        pass

    def __str__(self) -> str:
        return self.text

    def to_dict(self):
        return {
            'text': self.text,
            'single_table': self.single_table,
            'files': [file.to_dict() for file in self.files] if self.files else []
        }
    
    @classmethod
    def load(cls, draft_part_dict):
        text = draft_part_dict['text']
        single_table = draft_part_dict['single_table']
        files = {Chunk.load(file) for file in draft_part_dict['files']}
        return cls(text=text, single_table=single_table, files=files)