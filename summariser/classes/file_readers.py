
import pandas as pd
import tqdm
import os

class _Reader:
    def __init__(self, config_):
        self.config = config_
        self.items = []
    def main(self):
        self._set_subclass_variables()
        for self.file in tqdm.tqdm(os.listdir(self.config.folder)):
            if self.file.endswith(self.extension):
                self._read_file()
        self._make_df()

class TextReader(_Reader):
    def _set_subclass_variables(self):
        self.extension = '.txt'
    def _read_file(self):
        self.text = self.config.read(f'{self.config.folder}/{self.file}')
        self.items.append({
            'day': self.file[:-4], 
            'text': self.text, 
        })
    def _make_df(self):
        self.df = pd.DataFrame(self.items)

class DfReader(_Reader):
    def _set_subclass_variables(self):
        self.extension = '.csv'
    def _read_file(self):
        self.items.append(pd.read_csv(f'{self.config.folder}/{self.file}'))
    def _make_df(self):
        self.df = pd.concat(self.items)
        self.df.datetime = pd.to_datetime(self.df.datetime)
        self.df.date = self.df.datetime.dt.date
        
class DfCleanReader(DfReader):
    def _make_df(self):
        super()._make_df()
        self.df.translation = self.df.translation.map(lambda string: '\n'.join(string.split('\n')[2:]))
