import datetime
import pandas as pd

def seconds_to_time(chunk, index):
    dt = datetime.timedelta(seconds=chunk['timestamp'][index])
    time_split = str(dt).split('.') # . is before milliseconds
    # srt is French, so it uses comma, not full stop
    if len(time_split) == 1: # no milliseconds
        return time_split[0]+',000'
    elif len(time_split) == 2: # have milliseconds
        return time_split[0]+','+time_split[1][:3] # first 3 digits
    else:
        raise ValueError('timestamp format is incorrect')
format_sentence = lambda i, chunk: f'''
{i+1}
{seconds_to_time(chunk, 0)} --> {seconds_to_time(chunk, 1)}
{chunk['text'].strip()}'''

class DFFormatter:
    def __init__(self, config_):
        self.config = config_
    def main(self):
        self.df = pd.DataFrame(self.config.model_output['chunks'])
        self.df.to_csv(self.config.filename_out)
class SRTFormatter:
    def __init__(self, config_):
        self.config = config_
    def _fix_missing_last_timestamp(self):
        '''
        If there is silence at end of file, whisper returns null as last timestamp
        So I manually make the last subtitle last 1 seond
        '''
        self.last_timestamp = self.config.model_output['chunks'][-1]['timestamp']
        if self.last_timestamp[1] is None:
            self.last_timestamp = (self.last_timestamp[0], self.last_timestamp[0] + 1)
            self.config.model_output['chunks'][-1]['timestamp'] = self.last_timestamp
    def _format_text_as_srt(self):
        self.sentences = []
        for i, chunk in enumerate(self.config.model_output['chunks']):
            self.sentence = format_sentence(i = i, chunk = chunk)
            self.sentences.append(self.sentence)
        self.config.srt_contents = '\n'.join(self.sentences)
    def _write_srt(self):
        with open(self.config.filename_out, 'w') as file:
            file.write(self.config.srt_contents)
    def main(self):
        self._fix_missing_last_timestamp()
        self._format_text_as_srt()
        self._write_srt()
