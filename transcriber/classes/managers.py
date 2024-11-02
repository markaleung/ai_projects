import re, os, tqdm
from classes import models, formatters

class Config:
    pass

class FileRunner:
    def __init__(self, filename_in: str, model: str):
        self.config = Config()
        self.config.filename_in = filename_in
        self.config.filename_out = re.sub(r'.\w+$', '.txt', self.config.filename_in)
        self.config.device = 'mps'
        self.config.model = model
    def _extract_wav(self):
        self.wav = models.Wav(config_ = self.config)
        self.wav.main()
    def _run_model(self):
        self.model = models.Model(config_ = self.config)
        self.model.main()
        self.wav.delete_wav()
    def _format_srt(self):
        self.formatter = formatters.DFFormatter(config_ = self.config)
        self.formatter.main()
    def main(self):
        if os.path.exists(self.config.filename_out):
            return
        self._extract_wav()
        self._run_model()
        self._format_srt()

class FolderRunner:
    def __init__(self, folder: str, model: str):
        self.folder = folder
        self.model = model
    def _chdir(self):
        self.cwd = os.getcwd()
        os.chdir(self.folder)
        self.paths = [
            f'{folder}/{file}' for folder, _, files in os.walk('.') 
            for file in files if file[-3:] == 'mp3'
        ]
    def _run_file(self):
        self.file_runner = FileRunner(
            filename_in = self.path, 
            model=self.model, 
        )
        self.file_runner.main()
    def main(self):
        self._chdir()
        for self.path in tqdm.tqdm(self.paths):
            self._run_file()
        os.chdir(self.cwd)