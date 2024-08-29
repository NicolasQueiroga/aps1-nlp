from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class TFIDF:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None

    def fit_transform(self, documents):
        self.tfidf_matrix = self.vectorizer.fit_transform(documents).toarray().tolist()

    def get_similar_games(self, query, threshold=0.0):
        query_vector = self.vectorizer.transform([query])
        cosine_sim = cosine_similarity(query_vector, self.tfidf_matrix)
        indices = cosine_sim[0].argsort()[-1::-1]

        games = []
        for index in indices:
            if cosine_sim[0][index] > threshold:
                games.append(index)
            else:
                break

        return games
