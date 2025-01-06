import numpy as np
import pandas as pd
import addModules
import googleio

class Industries:
    def __init__(self, config_):
        self.config = config_
    def main(self):
        # self.industries_df = pd.read_csv(f'{self.config.book_name} - {self.config.sheet_name}.csv')
        self.df = googleio.read_gsheets(book_name = self.config.book_name, sheet_name = self.config.sheet_name)
        self.series = self.df['What industry do you work in?'].dropna()#.drop_duplicates()
        self.df = pd.DataFrame({'clean': self.config.vectoriser.clean_words(self.series), 'raw': self.series})
        # Remove blank industries
        self.names = [industry for industry in self.df.clean if industry]
        self.names, self.vectors = self.config.vectoriser.get_vectors(self.names)
        len(self.df), len(self.names), self.vectors.shape
        # Vectorised version of euclidean distance: (a-b)^2 = a^2 - 2ab + b^2
        self.sum_row = self.config.vectoriser.get_sum(self.vectors)
        self.sum = np.expand_dims(self.sum_row, axis = 1)

class Categories:
    def __init__(self, config_):
        self.config = config_
    def main(self):
        self.df = pd.DataFrame({'clean': self.config.vectoriser.clean_words(pd.Series(self.config.categories_raw)), 'raw': self.config.categories_raw})
        self.names, self.vectors = self.config.vectoriser.get_vectors(self.df.clean)
        len(self.df), len(self.names), self.vectors.shape
        self.sum = self.config.vectoriser.get_sum(self.vectors)

class Output:
    def __init__(self, config_):
        self.config = config_
    def main(self):
        self.df = pd.DataFrame({
            'industry': self.config.industries.names, 
            'industry_distance': self.config.metrics.argmin, 
            'distance': self.config.metrics.mins, 
            'industry_cosine': self.config.metrics.argmax, 
            'cosine': self.config.metrics.maxes, 
            'cluster': self.config.cluster.kmeans.labels_, 
            'cluster_distance': self.config.cluster.distances.min(axis = 1), 
        })
        for column in 'industry_distance', 'industry_cosine':
            self.df[column]= self.df[column].map(dict(enumerate(self.config.categories.names))).map(dict(self.config.categories.df.values))
        googleio.write_out(filename = self.config.book_name, tables = {'industry': self.df, 'industry_map': self.config.industries.df})
