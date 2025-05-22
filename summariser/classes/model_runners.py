import ollama
import tqdm

class Summariser:
    def __init__(self, day, df, config_):
        self.day = day
        self.df = df
        self.config = config_
        self._lines = []
        self._path = f'{self.config.folder}/{self.day}.txt'
    def _append_text(self):
        self._message = f'{self._row.datetime}\n{self._row.phone}\n{self._row.message}'
        self._lines.append(self._message)
    def _run_model(self):
        self._prompt = '\n\n'.join(self._lines)
        self._prompt = f'"{self._prompt}"\n\n{self.config.summarise}'
        self._response = ollama.generate(model=self.config.model, prompt=self._prompt)
        with open(self._path, 'w') as self._file:
            self._file.write(self._response['response'])
    def main(self):
        for self._row in self.df.itertuples():
            self._append_text()
        self._run_model()

class Translator:
    def __init__(self, day, df, config_):
        self.day = day
        self.df = df.set_index(['datetime', 'phone', 'date']).copy()
        self.df_short = self.df.query('translation != translation').copy()
        self.config = config_
        self.lines = []
        self._path = f'{self.config.folder}/{self.day}.csv'
    def _run_model(self):
        self._prompt = f'{self.config.translate}\n\n"{self._row.message}"'
        self._response = ollama.generate(model=self.config.model, prompt=self._prompt)
        return self._response['response']
    def _make_df(self):
        self.df_short['translation'] = self.lines
        self.df.loc[self.df_short.index, 'translation'] = self.df_short.translation
        self.df.drop('message', axis = 1).to_csv(self._path)
    def main(self):
        for self._row in tqdm.tqdm(self.df_short.itertuples(), total = len(self.df_short)):
            self.lines.append(self._run_model())
        self._make_df()
