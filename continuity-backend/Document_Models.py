from datetime import datetime


class Project:
    def __init__(self, name, description):
        self.id = None
        self.name = name
        self.description = description
        self.created_at = datetime.now().timestamp()

class Story:
    def __init__(self, project_id, title, body):
        self.id = None
        self.project_id = project_id
        self.title = title
        self.body = body


class Event:
    def __init__(self, story_id, name, description, participants: list[str]):
        self.id = None
        self.story_id = story_id
        self.name = name
        self.description = description
        self.participants = participants