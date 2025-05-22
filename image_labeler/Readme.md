# How to Install the Repository
- Install python, with an optional virtual environment
- Type `pip install requirements.txt`

# How to Run the Repository
- Type `jupyter notebook`
- Run Summariser.ipynb

# How to View the Streamlit
- Type `streamlit run <folder>`
- <folder> is where your photos are

# Composition Tree
- manager
    - read_files: jpegs not labelled yet
    - for filename in filenames:
        - run_model: 1 row per label from hugging face
    - make_df: rows from model
    - write_out: to csv
