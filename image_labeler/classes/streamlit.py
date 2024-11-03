import os
import pandas as pd
import streamlit as st
import sys

class ImageNet:
    def _read_df(self):
        os.chdir(os.path.dirname(__file__))
        self.df = pd.read_csv('../files_output/labels.csv')
    def _get_label(self):
        self.grouped = (
            self.df.groupby('label').size()
            .to_frame('size_').reset_index()
            .sort_values('size_', ascending = False)
            .query('size_ > 15')
        )
        self.grouped['combined'] = self.grouped.size_.astype(str) + ' ' + self.grouped.label
        self.grouped = self.grouped.sample(1, weights = self.grouped.size_)
        self.label = self.grouped.label.values[0]
    def _get_paths(self):
        self.df_filtered = self.df.query('label == @self.label')
        self.filenames = (
            self.df_filtered.sort_values('score', ascending = False)
            .sample(15, weights = self.df_filtered.score)
            .filename
        )
        self.paths = [
            f'{sys.argv[1]}/{filename}'
            for filename in self.filenames
        ]
    def _write(self):
        st.write(self.grouped.combined.values[0])
        self.col1, self.col2, self.col3 = st.columns(3)
        with self.col1:
            st.image(self.paths[0:5])
        with self.col2:
            st.image(self.paths[5:10])
        with self.col3:
            st.image(self.paths[10:15])
    def main(self):
        self._read_df()
        self._get_label()
        self._get_paths()
        self._write()

if __name__=='__main__':
    ImageNet().main()