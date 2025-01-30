# How to Install the Repository
- Install python, with an optional virtual environment
- Type `pip install requirements.txt`

# How to Run the Repository
- Type `jupyter notebook`
- Run notebook.ipynb

# Composition Tree
- managers.FolderRunner
    - managers.FileRunner
        - models.Wav: ffmpeg, write to temp.wav
        - models.Model: hugging face
        - formatters.DFFormatter: write dataframe to csv
        - formatters.SRTFormatter: use SRT template

