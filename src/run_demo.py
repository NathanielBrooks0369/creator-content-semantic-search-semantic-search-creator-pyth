import os

from semantic_search_service import ContentItem, InfraiClient, index_content, search_content


def main() -> None:
    client = InfraiClient()
    collection = os.environ.get("INFRAI_COLLECTION", "creator-content")
    item = ContentItem("welcome-pack", "A downloadable launch checklist for video creators", "supporter")
    index_content(client, collection, item)
    print(search_content(client, collection, "launch checklist", "supporter"))


if __name__ == "__main__":
    main()

