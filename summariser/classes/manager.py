import abc
import tqdm
import os
import addModules, googleio
from classes import table_maker, model_runners, file_readers

class Config:
    def __init__(self, conv_name):
        self.conv_name = conv_name
        self.model = 'llama3.2:1b'
        self.folder = f"files_output/{self.model.replace(':', '_')} {self.conv_name}"
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.file_chat = f'files_input/WhatsApp Chat with {self.conv_name}.txt'
        self.file_df = f'files_output/messages {self.conv_name}.csv'
        self.file_phone = f'files_input/phone_name {self.conv_name}.csv'
        self.summarise = 'summarise the above WhatsApp conversation in English'
        self.translate = 'Translate the following message into English:'
    def read(self, filename):
        with open(filename) as self.file:
            return self.file.read()

class Manager(abc.ABC):
    def __init__(self, config_):
        self.config = config_
    def _make_table(self):
        print('make table')
        # if not hasattr(self.config, '_table_maker'):
        self._table_maker = table_maker.TableMaker(config_ = self.config)
        self._table_maker.main()
    def _read_dfs(self):
        print('read files')
        # if not hasattr(self.config, '_file_reader'):
        self._df_reader = file_readers.DfReader(config_ = self.config)
        self._df_reader.main()
    def _join_dfs(self):
        print('join tables')
        if hasattr(self._df_reader, 'df'):
            self._join = (
                self._table_maker.df.merge(self._df_reader.df, how = 'left')
            )
        else:
            self._join = self._table_maker.df
            self._join['translation'] = float('nan')
        print('run model')
    def _run_model(self):
        self._model = self._model_class(
            day = self.day, df = self.df_day, config_ = self.config
        )
        self._model.main()
    def _read_files(self):
        print('read files')
        # if not hasattr(self.config, '_file_reader'):
        self._file_reader = self._reader_class(config_ = self.config)
        self._file_reader.main()
    def _upload_dfs(self):
        print('upload dfs')
        googleio.write_out('City Garden Conversations', {
            self._name: self._file_reader.df, 
            'messages': self._table_maker.df, 
        })
    def main(self):
        self._set_subclass_variables()
        self._make_table()
        self._read_dfs()
        self._join_dfs()
        for self.day, self.df_day in self._tqdm(self._join.groupby('date')):
            self._run_model()
        self._read_files()
        self._upload_dfs()

class Translator(Manager):
    def _set_subclass_variables(self):
        self._model_class = model_runners.Translator
        self._reader_class = file_readers.DfCleanReader
        self._name = 'translations'
        self._tqdm = lambda x: x
class Summariser(Manager):
    def _set_subclass_variables(self):
        self._model_class = model_runners.Summariser
        self._reader_class = file_readers.TextReader
        self._name = 'summaries'
        self._tqdm = lambda x: tqdm.tqdm(x)
