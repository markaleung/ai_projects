from datasets import Dataset, Audio
from transformers import pipeline
import subprocess
import os

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
