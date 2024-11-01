import datetime, subprocess, re, os, tqdm
import pandas as pd
from transformers import pipeline
from datasets import Dataset, Audio

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

class Config:
    pass

class Wav:
    def __init__(self, config_):
        self.config = config_
    def delete_wav(self):
        if os.path.exists('temp.wav'):
            os.remove('temp.wav')
    def extract_wav(self):
        subprocess.run([
            '/opt/homebrew/bin/ffmpeg', '-i', self.config.filename_in, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', 'temp.wav'
        ], stdout = subprocess.DEVNULL, stderr=subprocess.STDOUT)
    def main(self):
        self.delete_wav()
        self.extract_wav()

class Model:
    def __init__(self, config_):
        self.config = config_
    def import_wav(self):
        self.audio_dataset = Dataset.from_dict({"audio": ['temp.wav']}).cast_column("audio", Audio())
        self.pipe = pipeline(
            "automatic-speech-recognition", 
            model = self.config.model, 
            chunk_length_s=30, 
            device=self.config.device
        )
        self.pipe.model.config.forced_decoder_ids = self.pipe.tokenizer.get_decoder_prompt_ids(language='yue', task="transcribe")
    def run_model(self):
        self.config.model_output = self.pipe(
            self.audio_dataset[0]['audio']['array'], 
            batch_size=8,
            return_timestamps=True,
            generate_kwargs={"task": "transcribe"},
            # max_new_tokens=256,
        )
    def main(self):
        self.import_wav()
        self.run_model()

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

class FileRunner:
    def __init__(self, filename_in: str, model: str):
        self.config = Config()
        self.config.filename_in = filename_in
        self.config.filename_out = re.sub(r'.\w+$', '.txt', self.config.filename_in)
        self.config.device = 'mps'
        self.config.model = model
    def _extract_wav(self):
        self.wav = Wav(config_ = self.config)
        self.wav.main()
    def _run_model(self):
        self.model = Model(config_ = self.config)
        self.model.main()
        self.wav.delete_wav()
    def _format_srt(self):
        self.formatter = DFFormatter(config_ = self.config)
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