from datetime import datetime

import openai
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from feed.models import PrivateFeed


# 유저 임베딩 벡터 계산 로직들
def get_user_interest_embedding(user_interests):
    # 각 제목에 대한 임베딩 벡터 생성
    def get_embeddings(interest_keywords):
        embeddings = []
        for title in interest_keywords:
            response = openai.Embedding.create(
                model="text-similarity-babbage-001",
                input=title
            )
            embeddings.append(response['data'][0]['embedding'])
        return embeddings

    # 임베딩을 기반으로 클러스터링 수행
    def group_and_weight_embeddings(embeddings):
        kmeans = KMeans(n_clusters=5)
        kmeans.fit(embeddings)
        labels = kmeans.labels_
        weights = [list(labels).count(i) for i in range(kmeans.n_clusters)]
        return labels, weights

    # 가중 평균 임베딩 벡터 계산
    def calculate_weighted_average_embedding(embeddings, labels, weights):
        cluster_embeddings = [[] for _ in range(len(set(labels)))]
        for embedding, label in zip(embeddings, labels):
            cluster_embeddings[label].append(embedding)
        weighted_embeddings = []
        for cluster, weight in zip(cluster_embeddings, weights):
            weighted_embeddings.append(np.mean(cluster, axis=0) * weight)
        final_embedding = np.sum(weighted_embeddings, axis=0) / sum(weights)
        return final_embedding

    embeddings = get_embeddings(user_interests)
    labels, weights = group_and_weight_embeddings(embeddings)
    weighted_embedding = calculate_weighted_average_embedding(embeddings, labels, weights)

    return weighted_embedding


# 기사 임베딩 벡터 계산 로직
def get_article_embeddings(user):
    today = datetime.now().date()
    articles = PrivateFeed.objects.filter(user=user, date=today)[:30]

    article_embeddings = {}
    for article in articles:
        response = openai.Embedding.create(
            model="text-similarity-babbage-001",
            input=article.content
        )
        embedding_vector = response['data'][0]['embedding']
        article_embeddings[article.title] = embedding_vector

    return article_embeddings


def find_closest_articles(user_embedding, articles_embeddings):
    similarities = {}
    for title, embedding in articles_embeddings.items():
        similarity = cosine_similarity([user_embedding], [embedding])[0][0]
        similarities[title] = similarity

    n = 3
    closest_titles = sorted(similarities, key=similarities.get, reverse=True)[:n]

    return closest_titles
