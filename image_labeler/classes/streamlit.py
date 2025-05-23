import os
import pandas as pd
import streamlit as st
import sys

class ImageNet:
    def _read_df(self):
        os.chdir(os.path.dirname(__file__))
        self.df = pd.read_csv('../files_output/labels.csv')
    def _set_variables_ui(self):
        if st.button('Refresh'):
            st.rerun()
        self.threshold = st.number_input(
            'Threshold', min_value = 0.0, max_value = 1.0, value = 0.1
        )
        self.mode = st.radio(
            'Choose Label', ['Random', 'Dropdown'], horizontal = True
        )
    def _filter_and_group_df(self):
        self.df = self.df.query('score > @self.threshold')
        self.grouped = (
            self.df.groupby('label').size()
            .to_frame('size_').reset_index()
            .sort_values('size_', ascending = False)
            .query('size_ > 15')
        )
        self.grouped['combined'] = self.grouped.size_.astype(str) + ' ' + self.grouped.label
    def _get_label_random(self):
        self.grouped2 = self.grouped.sample(1, weights = self.grouped.size_)
        self.label = self.grouped2.label.values[0]
    def _get_label_dropdown(self):   
        self.label = st.selectbox('Label', self.grouped.label)
        self.grouped2 = self.grouped.query('label == @self.label')
    def _get_label(self):
        if self.mode == 'Random':
            self._get_label_random()
        else:
            self._get_label_dropdown()
        st.write(self.grouped2.combined.values[0])
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
        self.col1, self.col2, self.col3 = st.columns(3)
        with self.col1:
            st.image(self.paths[0:5])
        with self.col2:
            st.image(self.paths[5:10])
        with self.col3:
            st.image(self.paths[10:15])
    def main(self):
        self._read_df()
        with st.sidebar:
            self._set_variables_ui()
            self._filter_and_group_df()
            self._get_label()
        self._get_paths()
        self._write()

if __name__=='__main__':
    ImageNet().main()