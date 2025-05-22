# How to Install the Repository
- Install python, with an optional virtual environment
- Type `pip install requirements.txt`

# How to Prepare files_input
- Export the whatsapp conversation (see WhatsApp Chat with John Doe.txt)
- Map phone numbers to names (see phone_name John Doe.csv)

# How to Run the Repository
- Type `jupyter notebook`
- Run Summariser.ipynb

# Composition Tree
- manager
    - table_maker: parse lines in whatsapp, join phone names
    - df_reader: get existing translations
    - join_dfs: check for missing translations
    - for day, df_day in join.groupby('date'):
        - model_runner: only if translations are missing
    - file_reader: read model output

# Inheritance Tree
- manager.Manager: choose model, reader classes
    - Translator: translate each message
    - Summariser: summarise joined messages
- file_readers.Reader
    - TextReader: one line per text file
    - DfReader: concat csv files
        - DfCleanReader: remove translation headers
