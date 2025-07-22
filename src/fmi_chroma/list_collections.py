import sys

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import chromadb  # noqa: E402


def list_collections():
    """Lists all collections in the Chroma database."""
    client = chromadb.HttpClient(host="chroma", port=8000)
    collections = client.list_collections()
    for collection in collections:
        print(collection.name)


if __name__ == "__main__":
    list_collections()
