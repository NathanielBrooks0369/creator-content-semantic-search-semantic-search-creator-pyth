import os

from semantic_search_service import InfraiClient, search_content


def main() -> None:
    client = InfraiClient()
    collection = os.environ["INFRAI_COLLECTION"]
    print(search_content(client, collection, "launch checklist", "supporter"))


if __name__ == "__main__":
    main()
