import argparse
import os
import sys

from langchain.text_splitter import RecursiveCharacterTextSplitter

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import chromadb  # noqa: E402


def add_texts_from_directory(
    directory_path: str,
    collection_name: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
):
    # Initialize Chroma HTTP client
    client = chromadb.HttpClient(host="chroma", port=8000)

    # Get or create the specified collection
    collection = client.get_or_create_collection(name=collection_name)

    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    # Define the file extensions to search for (lowercase for matching)
    extensions = ["md", "txt", "adoc", "c", "h", "rst", "py"]
    extensions_set = {ext.lower() for ext in extensions}

    file_count = 0
    chunk_count = 0

    # Walk the directory tree once
    for root, _, files in os.walk(directory_path):
        for filename in files:
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if ext in extensions_set:
                filepath = os.path.join(root, filename)
                file_count += 1
                with open(filepath, encoding="utf-8", errors="ignore") as file:
                    full_text = file.read()
                    chunks = text_splitter.split_text(full_text)
                    file_id_base = os.path.abspath(filepath)
                    chunk_ids = []
                    chunk_metadatas = []
                    for i, _chunk in enumerate(chunks):
                        chunk_ids.append(f"{file_id_base}_chunk_{i}")
                        chunk_metadatas.append({
                            "filename": filename,
                            "chunk_index": i,
                        })
                    if chunks:
                        collection.add(
                            documents=chunks,
                            ids=chunk_ids,
                            metadatas=chunk_metadatas,
                        )
                        chunk_count += len(chunks)
                        print(
                            f"Added {len(chunks)} chunks from {filename} to collection '{collection_name}'."
                        )

    if file_count == 0:
        print("No text files found in the specified directory.")
    else:
        print(
            f"Added total {chunk_count} chunks from {file_count} files to collection '{collection_name}'."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add text files from a directory to a Chroma collection."
    )
    parser.add_argument(
        "--directory_path",
        type=str,
        default="/workspaces/fmi-chroma/.chroma/text",
        help="The directory containing text files to add.",
    )
    parser.add_argument(
        "--collection_name",
        type=str,
        default="FMI_documents",
        help="The name of the Chroma collection.",
    )
    args = parser.parse_args()
    add_texts_from_directory(args.directory_path, args.collection_name)
