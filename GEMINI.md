# Gemini Agent Rules

- When answering questions about FMI, I must first query the `FMI_documents` Chroma collection. If the search returns no relevant results, I must inform the user of this before answering from my general knowledge.
- When answering What/How/Which questions, only print out the answer and do not perform any modifications until an explicit request to execute.
- I am working in a devcontainer. Never modify the temporary configuration files under /home/vscode. Always modify the configuration in the current directory.
