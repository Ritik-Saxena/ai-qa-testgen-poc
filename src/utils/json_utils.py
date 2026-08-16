import json
from pathlib import Path

class JsonUtils:
    
    def __init__(self, jira_story):
        self.jira_story = jira_story

    def json_writer(self, json_data, file_name=None):
        self.file_path = f"output/{self.jira_story}/{file_name}.json"
        out = Path(self.file_path)

        out.parent.mkdir(parents=True, exist_ok=True)

        response = json.loads(json_data)
        out.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")

    
    def json_reader(self, file_name=None):
        self.file_path = f"output/{self.jira_story}/{file_name}.json"
        out = Path(self.file_path)

        if not out.exists():
            raise FileNotFoundError(f"File {self.file_path} does not exist.")

        with open(out, "r", encoding="utf-8") as file:
            data =  json.load(file)

        return data

