# %%
import sys

# workaround for wrong sqlite version in the image
# see: https://stackoverflow.com/a/79591669/1427080
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")


if __name__ == "__main__":
    sys.argv = [
        "chroma-mcp",
        "--client-type",
        "http",
        "--host",
        "chroma",
        "--port",
        "8000",
        "--ssl",
        "false",
    ]
    from chroma_mcp import main

    sys.exit(main())

# %%
