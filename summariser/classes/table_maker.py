import re
import pandas as pd
import tqdm

class Parser:
    def __init__(self):
        self._regex_datetime = r'(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}) - '
        self._regex_phone = r'([^:]{1,20}): '
        self._regex_datetime_phone = self._regex_datetime + self._regex_phone
        self._datetime, self._phone, self._edited = '', '', ''
    def _handle_datetime(self):
        self._search_datetime = re.match(self._regex_datetime, self.raw)
        self._edited = re.sub('^' + self._regex_datetime, '', self.raw)
    def _handle_datetime_phone(self):
        self._datetime = self._search_datetime.group(1)
        self._search_datetime_phone = re.match(self._regex_datetime_phone, self.raw)
    def _handle_phone(self):
        self._phone = self._search_datetime_phone.group(2)
        self._edited = re.sub('^' + self._regex_phone, '', self._edited)
    def _make_dict(self):
        self.dict = {
            'datetime': self._datetime, 
            'phone': self._phone, 
            'edited': self._edited, 
            'raw': self.raw, 
        }
    def main(self):
        self._handle_datetime()
        if self._search_datetime:
            self._handle_datetime_phone()
            if self._search_datetime_phone:
                self._handle_phone()
            else:
                self._phone = 'WhatsApp'
        else:
            self._edited = self.raw
        self._make_dict()
        return self.dict

class TableMaker:
    def __init__(self, config_):
        self.config = config_
        self._dicts = []
    def _read_df(self):
        self._parser = Parser()
        self._messages = self.config.read(self.config.file_chat).split('\n')
        self.phones = dict(pd.read_csv(self.config.file_phone).values)
    def _make_df(self):
        self.df_raw = pd.DataFrame(self._dicts)
        self.df_raw.datetime = pd.to_datetime(self.df_raw.datetime, format = "%d/%m/%Y, %H:%M")
        self.df_raw['date'] = self.df_raw.datetime.dt.date
    def _map_phone_names(self):
        self.missing = sorted(set(self.df_raw.phone.unique()) ^ set(self.phones.keys()))
        if len(self.missing) > 0:
            print('\n'.join(self.missing))
            raise Exception(f'{len(self.missing)} are missing')
        self.df_raw.phone = self.df_raw.phone.map(lambda phone: self.phones[phone])
    def _group_df(self):
        self.df = (
            self.df_raw.groupby(['datetime', 'phone', 'date'])
            .apply(lambda df: '\n'.join(df.edited))
            .to_frame('message').reset_index()
        )
        self.df.to_csv(self.config.file_df, index = False)
        self.df_group = self.df.groupby('date').size().to_frame('tm').reset_index()
    def main(self):
        self._read_df()
        for self._parser.raw in tqdm.tqdm(self._messages):
            self._dicts.append(self._parser.main())
        self._make_df()
        self._map_phone_names()
        self._group_df()
