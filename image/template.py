import json
import traceback
from typing import Union, List
from fuzzywuzzy import process
from image.types import Template, TextField


class TemplateManager:
    def __init__(self):
        self.templates: List[Template] = []

    @staticmethod
    def parse_template(data: json) -> Template:
        return Template(name=data["name"],
                        labels=[],
                        file=data["image"],
                        id=data["id"],
                        creator=data["creator"],
                        createdAt=data["createdAt"],
                        fields={
                            "text": [
                                TextField(
                                    posX=f["x"],
                                    posY=f["y"],
                                    width=f["width"],
                                    height=f["height"],
                                    align=f["textProps"]["align"],
                                    color=f["textProps"]["color"],
                                    font_size=f["textProps"]["fontSize"],
                                    bold=f["textProps"]["bold"],
                                    outlinePercentage=f["shadowProps"]["percentage"] if f["shadowProps"]["enabled"] else 0,
                                    outlineColor=f["shadowProps"]["color"],
                                ) for f in data["fields"]],
                            "images": [],
                        })

    def load_templates(self):
        print("⏳ Loading templates…")
        self.templates = []
        count = 0
        with open("assets/templates/index.json") as c:
            json_ = json.loads(c.read())
            for template in json_:
                if template["verified"]:
                    try:
                        with open(f"./assets/templates/{template['file']}") as f:
                            template = self.parse_template(json.loads(f.read()))
                            self.templates.append(template)
                            print(f"> Loaded template '{template.name}' successfully")
                            count += 1
                    except Exception as e:
                        print(f"> Couldn't load template '{template['name']}' due to {e}")
                        print("\n".join(traceback.format_exception(type(e), e, e.__traceback__)))

        print(f"✅ Done loading {count} templates.")

    def find_template(self, query: str) -> Union[Template, None]:
        return next((t for t in self.templates if t.name == query), None)

    def search_template(self, query: str) -> List[tuple]:
        choices = [x.name for x in self.templates]
        return process.extractBests(query, choices, score_cutoff=50)

