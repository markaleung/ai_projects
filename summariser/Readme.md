# How to Install the Repository
- Install python, with an optional virtual environment
- Type `pip install requirements.txt`

# How to Run the Repository
- Type `jupyter notebook`
- Run Summariser.ipynb

# Composition Tree
- manager
    - table_maker
    - reader
    - model_runners

# Inheritance Tree
- manager.Manager
    - Translator
    - Summariser
- file_readers.Reader
    - TextReader
    - DfReader
    - DfCleanReader
