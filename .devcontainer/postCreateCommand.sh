#! /usr/bin/env bash

# Install uv
# curl -LsSf https://astral.sh/uv/install.sh | sh

#
cd /home/vscode/
mkdir -p .codeium/windsurf/
ln -s /workspaces/fmi-chroma/.windsurf/mcp_config.json .codeium/windsurf/mcp_config.json
ln -s /workspaces/fmi-chroma/.windsurf

cd /workspaces/fmi-chroma/

# Install Dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install --install-hooks

# Install Gemini CLI
npm install -g @google/gemini-cli

source .venv/bin/activate

# Add FMI documents to Chroma if collection does not exist
if ! python -m fmi_chroma.list_collections | grep -q "FMI_documents"; then
    echo "FMI_documents collection not found. Adding documents."
    python -m fmi_chroma.git2chroma
else
    echo "FMI_documents collection already exists. Skipping."
fi

# Add OpenModelica documents to Chroma if collection does not exist
if ! python -m fmi_chroma.list_collections | grep -q "OpenModelica_documents"; then
    echo "OpenModelica_documents collection not found. Adding documents."
    python -m fmi_chroma.git2chroma --repo_url "https://github.com/OpenModelica/OpenModelica" --tag "v1.25.1" --collection_name "OpenModelica_documents"
else
    echo "OpenModelica_documents collection already exists. Skipping."
fi
