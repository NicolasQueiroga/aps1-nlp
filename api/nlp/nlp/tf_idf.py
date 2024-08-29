from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class TFIDF:
    def __init__(self, corpus):
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None
        self.ids, self.documents = zip(*corpus)

    def fit_transform(self):
        self.tfidf_matrix = (
            self.vectorizer.fit_transform(self.documents).toarray().tolist()
        )

    def get_similar_games(self, query, threshold=0.0):
        query_vector = self.vectorizer.transform([query])
        cosine_sim = cosine_similarity(query_vector, self.tfidf_matrix)

        games = []
        for i, sim in enumerate(cosine_sim[0]):
            if sim > threshold:
                games.append((self.ids[i], sim))

        return games if games else [(None, None)]
