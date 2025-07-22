#! /usr/bin/env bash

# Install uv
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install --install-hooks

# Install Gemini CLI
npm install -g @google/gemini-cli

# Add FMI documents to Chroma if collection does not exist
if ! python -m fmi_chroma.list_collections | grep -q "FMI_documents"; then
    echo "FMI_documents collection not found. Adding documents."
    python -m fmi_chroma.git2chroma
else
    echo "FMI_documents collection already exists. Skipping."
fi
