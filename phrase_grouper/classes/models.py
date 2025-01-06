from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.cluster import KMeans
import embeddings
import nltk
import numpy as np
import pandas as pd
import tqdm

class Vectoriser:
    def __init__(self, config_):
        self.config = config_
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.glove = embeddings.GloveEmbedding('common_crawl_840', d_emb=300, show_progress=True)
    def clean_words(self, series: pd.Series) -> pd.Series:
        # Punctuation
        series = series.str.replace('-', '').str.lower().fillna('').astype(str)
        series = series.str.replace('[^A-Za-z ]', ' ').str.lower().fillna('').astype(str)
        # Tokenise
        nltk.download('punkt_tab')
        series = series.apply(lambda x: nltk.word_tokenize(x))
        series = series.apply(lambda x: [word for word in x if word not in self.stop_words])
        nltk.download('wordnet')
        series = series.apply(lambda x: [self.lemmatizer.lemmatize(word) for word in x])
        exclude_words = [","]
        series = series.apply(lambda x: [word for word in x if word not in self.stop_words and word not in exclude_words])
        return series.map(lambda x: ' '.join(x)).values
    def get_vectors(self, rows):
        rows2 = []
        vectors = []
        for row in tqdm.tqdm(rows):
            output = []
            for word in row.split(' '):
                vector = self.glove.emb(word)
                if None in vector:
                    pass
                    # print(word)
                else:
                    output.append(vector)
            output = np.array([output]).mean(axis = 1)
            if output.shape == (1, 300):
                rows2.append(row)
                vectors.append(output)
        vectors = np.concatenate(vectors, axis = 0)
        return rows2, vectors
    def get_sum(self, array):
        return (array ** 2).sum(axis = 1)

class Metrics:
    def __init__(self, config_):
        self.config = config_
    def main(self):
        self.multiply = (
            self.config.industries.vectors @ self.config.categories.vectors.T
        )
        self.distances = np.sqrt(
            self.config.industries.sum + self.config.categories.sum 
            - 2 * self.multiply
        )
        self.cosines = (
            self.multiply / np.sqrt(self.config.industries.sum 
            * self.config.categories.sum)
        )
        self.argmin = self.distances.argmin(axis = 1)
        self.mins = self.distances.min(axis = 1)
        self.argmax = self.cosines.argmax(axis = 1)
        self.maxes = self.cosines.max(axis = 1)

class Cluster:
    def __init__(self, config_):
        self.config = config_
    def main(self):
        self.kmeans = KMeans(n_clusters = len(self.config.categories_raw))
        self.kmeans.fit(self.config.industries.vectors)
        self.labels = self.kmeans.labels_, 
        self.sum = self.config.vectoriser.get_sum(self.kmeans.cluster_centers_)
        self.multiply = (
            self.config.industries.vectors @ self.kmeans.cluster_centers_.T
        )
        self.distances = np.sqrt(
            self.config.industries.sum + self.sum - 2 * self.multiply
        )
