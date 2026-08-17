import os

from atlassian import Confluence

class ConfluenceClient:
    def __init__(self):
        self.confluence = Confluence(
            url=os.getenv("Atlassian_BASE_URL"),
            username=os.getenv("Atlassian_EMAIL"),
            password=os.getenv("Atlassian_API_TOKEN"),
            cloud=os.getenv("Atlassian_CLOUD", "true").lower() == "true"
        )

    def get_page_by_title(self, space_key, title):
        pages = self.confluence.get_all_pages_from_space(space_key, start=0, limit=100) or []
        for page in pages:
            if page.get("title") == title:
                return page
        return None

    def create_page(self, space, title, body, type="page", representation="storage"):
        return self.confluence.create_page(
            space=space,
            title=title,
            body=body,
            type=type,
            representation=representation,
        )

    def update_page(self, page_id, title, body, type="page", representation="storage"):
        return self.confluence.update_page(
            page_id=page_id,
            title=title,
            body=body,
            type=type,
            representation=representation,
        )
