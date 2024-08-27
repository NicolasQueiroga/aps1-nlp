import numpy as np


class TFIDF:
    def __init__(self, corpus):
        self.corpus = corpus
        self.idf = {}
        self.tf = {}
        self.tfidf = {}

    def fit(self):
        for document in self.corpus:
            for word in document:
                if word not in self.idf:
                    self.idf[word] = 0
                self.idf[word] += 1

        for word in self.idf:
            self.idf[word] = np.log(len(self.corpus) / self.idf[word])

        for i, document in enumerate(self.corpus):
            self.tf[i] = {}
            for word in document:
                if word not in self.tf[i]:
                    self.tf[i][word] = 0
                self.tf[i][word] += 1

            for word in self.tf[i]:
                self.tf[i][word] = self.tf[i][word] / len(document)

        for i, document in enumerate(self.corpus):
            self.tfidf[i] = {}
            for word in document:
                self.tfidf[i][word] = self.tf[i][word] * self.idf[word]

    def query(self, query):
        query_vector = {}
        for word in query:
            if word not in query_vector:
                query_vector[word] = 0
            query_vector[word] += 1

        for word in query_vector:
            query_vector[word] = query_vector[word] / len(query)

        scores = []
        for i in range(len(self.corpus)):
            score = 0
            for word in query_vector:
                if word in self.tfidf[i]:
                    score += query_vector[word] * self.tfidf[i][word]
            scores.append(score)

        return scores
