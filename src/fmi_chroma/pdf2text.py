import argparse
import os

from PyPDF2 import PdfReader


def convert_pdf_to_text(source_dir, dest_dir):
    """
    Converts all PDF files in the source directory to text files in the destination directory.

    Args:
        source_dir (str): The path to the directory containing the PDF files.
        dest_dir (str): The path to the directory where the text files will be saved.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for filename in os.listdir(source_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(source_dir, filename)
            text_path = os.path.join(
                dest_dir, os.path.splitext(filename)[0] + ".txt"
            )

            try:
                with open(pdf_path, "rb") as pdf_file:
                    reader = PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()

                with open(text_path, "w", encoding="utf-8") as text_file:
                    text_file.write(text)

                print(f"Successfully converted {filename} to text.")
            except Exception as e:
                print(f"Error converting {filename}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert PDF files to text documents."
    )
    parser.add_argument(
        "--source",
        default="/workspaces/fmi-chroma/.chroma/src",
        help="The source directory containing PDF files.",
    )
    parser.add_argument(
        "--destination",
        default="/workspaces/fmi-chroma/.chroma/text",
        help="The destination directory for the text files.",
    )
    args = parser.parse_args()

    convert_pdf_to_text(args.source, args.destination)
