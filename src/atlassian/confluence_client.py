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
        
    def create_or_update_page(self, space_key, title, body):
        page = self.confluence.get_page_by_title(space_key, title)

        if page:
            page = self.confluence.update_page(
                page_id=page["id"],
                title=title,
                body=body,
                type="page",
                representation="storage"
            )
        else:
            page = self.confluence.create_page(
                space=space_key,
                title=title,
                body=body,
                type="page",
                representation="storage"
            )

        return page