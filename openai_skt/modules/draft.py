class Draft:
    def __init__(self, draft='', purpose=None, table=None, files=None):
        self.draft = draft
        self.purpose = purpose
        self.table = table
        self.files = files

    def edit(self):
        pass


class DraftPart:
    def __init__(self, draft_part='', purpose=None, table=None, files=None):
        self.draft_part = draft_part
        self.purpose = purpose
        self.table = table
        self.files = files

    def edit(self):
        pass