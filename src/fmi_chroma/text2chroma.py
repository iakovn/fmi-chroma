import argparse
import glob
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

    # Define the file extensions to search for
    extensions = ["md", "txt", "adoc", "c", "h"]

    all_chunks = []
    all_ids = []
    all_metadatas = []

    file_count = 0

    # Recursively search for files with the specified extensions
    for extension in extensions:
        # Search for both lowercase and uppercase extensions
        for filepath in glob.glob(
            os.path.join(directory_path, f"**/*.{extension}"), recursive=True
        ):
            file_count += 1
            with open(filepath, encoding="utf-8", errors="ignore") as file:
                full_text = file.read()
                chunks = text_splitter.split_text(full_text)
                file_id_base = os.path.abspath(filepath)

                for i, chunk in enumerate(chunks):
                    all_chunks.append(chunk)
                    all_ids.append(f"{file_id_base}_chunk_{i}")
                    all_metadatas.append({
                        "filename": os.path.basename(filepath),
                        "chunk_index": i,
                    })

    if not all_chunks:
        print("No text files found in the specified directory.")
        return

    collection.add(documents=all_chunks, ids=all_ids, metadatas=all_metadatas)
    print(
        f"Added {len(all_chunks)} chunks from {file_count} files to collection '{collection_name}'."
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
