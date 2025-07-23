import argparse
import os
import shutil
import subprocess

from fmi_chroma.text2chroma import add_texts_from_directory


def clone_repo(repo_url, tag, dest_dir):
    """
    Clones a specific tag from a git repository with depth 1.

    Args:
        repo_url (str): The URL of the git repository.
        tag (str): The tag to clone.
        dest_dir (str): The destination directory for the clone.
    """
    if os.path.exists(dest_dir):
        print(f"Directory {dest_dir} already exists. Removing it.")
        shutil.rmtree(dest_dir)

    command = [
        "git",
        "clone",
        "--single-branch",
        "--depth",
        "1",
        "--branch",
        tag,
        repo_url,
        dest_dir,
    ]

    try:
        print(f"Cloning {repo_url} tag {tag} to {dest_dir}...")
        subprocess.run(command, check=True, capture_output=True, text=True)  # noqa: S603
        print("Clone successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Clone a git repository and add its text files to a Chroma collection."
    )
    parser.add_argument(
        "--repo_url",
        type=str,
        default="https://github.com/modelica/fmi-standard/",
        help="The URL of the git repository to clone.",
    )
    parser.add_argument(
        "--tag",
        type=str,
        default="v2.0.5",
        help="The git tag to clone.",
    )
    parser.add_argument(
        "--collection_name",
        type=str,
        default="FMI_documents",
        help="The name of the Chroma collection.",
    )
    args = parser.parse_args()

    clone_dir = os.path.join(
        ".chroma", os.path.basename(args.repo_url) + f"_{args.tag}"
    )

    try:
        clone_repo(args.repo_url, args.tag, clone_dir)
        add_texts_from_directory(clone_dir, args.collection_name)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
