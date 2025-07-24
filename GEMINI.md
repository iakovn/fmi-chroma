# Gemini Agent Rules

- When answering questions about FMI, I must first query the `FMI_documents` Chroma collection. If the search returns no relevant results, I must inform the user of this before answering from my general knowledge.
- When answering What/How/Which questions, only print out the answer and do not perform any modifications until an explicit request to execute.
- I am working in a devcontainer. Never modify the temporary configuration files under /home/vscode. Always modify the configuration in the current directory.
- Before modifying the code make sure there are no outstanding non-committed changes. Ask user to commit before applying any change.
- After generating code automatically run precommit hooks and fix any errors.
- After modifying demo.py notebook, update ipynb file and clear outputs using the commands:
```
    jupytext --sync src/fmi_chroma/notebooks/demo.py
    jupyter nbconvert --ClearOutputPreprocessor.enabled=True --to notebook --inplace src/fmi_chroma/notebooks/demo.ipynb
```
- The project is using pytest as test runner (not unittest)
- The project uses ruff as linter
- Always generate type definitions. The project will be checked with mypy.
- use uv to manage dependencies.
