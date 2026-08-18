from src.clients.atlassian.confluence_client import ConfluenceClient

class ConfluenceService:
    def __init__(self):
        self.confluence_client = ConfluenceClient()

    def create_or_update_page(self, space_key, title, body):
        page = self.confluence_client.get_page_by_title(space_key, title)

        if page:
            page = self.confluence_client.update_page(
                page_id=page["id"],
                title=title,
                body=body,
                type="page",
                representation="storage"
            )
        else:
            page = self.confluence_client.create_page(
                space=space_key,
                title=title,
                body=body,
                type="page",
                representation="storage"
            )

        return page