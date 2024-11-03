from transformers import pipeline
from PIL import Image
import pandas as pd, tqdm
import os

class Config:
    def __init__(self):
        self.dict_list = []
        self.batch_size = 100
class ConfigCaption(Config):
    def __init__(self):
        super().__init__()
        self.filename_csv = 'files_output/captions.csv'
        self.model_class = Caption
class ConfigLabel(Config):
    def __init__(self):
        super().__init__()
        self.filename_csv = 'files_output/labels.csv'
        self.model_class = Label
CONFIGS = {'Caption': ConfigCaption, 'Label': ConfigLabel}

class Caption:
    def __init__(self, config_):
        self.config = config_
    def _get_caption(self):
        self.captioner = pipeline("image-to-text",model="Salesforce/blip-image-captioning-base")    
        self.caption = self.captioner(f"{self.config.folder_in}/{self.config.filename}")[0]['generated_text']
        self.config.dict_list.append({'filename': self.config.filename, 'caption': self.caption})
    def main(self):
        self._get_caption()
class Label:
    def __init__(self, config_):
        self.config = config_
    def _get_labels(self):
        self.img = Image.open(f"{self.config.folder_in}/{self.config.filename}")
        self.classifier = pipeline("image-classification", model="google/vit-base-patch16-224", device = 'mps')
        self.labels = self.classifier(self.img)
    def _append_label(self):
        self.label.update({'filename': self.config.filename})
        self.config.dict_list.append(self.label)
    def main(self):
        self._get_labels()
        for self.label in self.labels:
            self._append_label()

class Manager:
    def __init__(self, folder_in: str, config_class):
        self.config_class = config_class
        self.config = CONFIGS[self.config_class]()
        self.config.folder_in = folder_in
    def _read_files(self):
        self.df_in = pd.read_csv(self.config.filename_csv)
        self.filenames = [
            filename for filename in os.listdir(self.config.folder_in) 
            if filename.lower().split('.')[-1] in {'jpeg', 'jpg'}
        ]
        self.filenames = sorted(set(self.filenames) - set(self.df_in.filename))
    def _run_model(self):
        self.model = self.config.model_class(config_ = self.config)
        self.model.main()
    def _make_df(self):
        self.df_new = pd.DataFrame(self.config.dict_list)
        self.df = pd.concat([self.df_in, self.df_new])
    def _write_out(self):
        self.df.to_csv(self.config.filename_csv, index = False)
    def main(self):
        self._read_files()
        if len(self.filenames) == 0:
            return 'empty'
        for self.config.filename in tqdm.tqdm(self.filenames[0:self.config.batch_size]):
            self._run_model()
        self._make_df()
        self._write_out()
        return 'not empty'
    