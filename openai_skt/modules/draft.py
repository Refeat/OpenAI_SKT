from typing import Any

class Draft:
    def __init__(self, purpose=None, tables=None):
        self.text = ''
        self.draft_parts = list()
        self.purpose = purpose
        self.tables = tables
        self.files = list() # [chunk1, chunk2, chunk3]

    def edit(self):
        pass

    def add_draft_part(self, draft_part):
        self.text += draft_part.text + '\n'
        self.files += draft_part.files
        self.draft_parts.append(draft_part)
    
    def __str__(self) -> str:
        return self.text

    def to_dict(self):
        return {
            'text': self.text,
            'purpose': self.purpose,
            'tables': self.tables,
            'draft_parts': [draft_part.to_dict() for draft_part in self.draft_parts] if self.draft_parts else []
        }

class DraftPart:
    def __init__(self, text=None, purpose=None, single_table=None, files=None):
        self.text = text
        self.purpose = purpose
        self.single_table = single_table
        self.files = files

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