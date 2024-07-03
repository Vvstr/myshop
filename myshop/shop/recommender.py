import numpy as np
import redis
from django.conf import settings
from .models import Product
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import matplotlib.pyplot as plt
import base64
from io import BytesIO


class Recommender:
    def __init__(self, products):
        self.products = products
        self.kg = nx.Graph()
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.redis_client = redis.StrictRedis(host=settings.REDIS_HOST,
                                              port=settings.REDIS_PORT,
                                              db=settings.REDIS_DB)

    def build_knowledge_graph(self):
        # Добавляем продукты в виде нодов(Nodes)
        for product in self.products:
            self.kg.add_node(product.id, description=product.description, category=product.category.id)

    def fit(self):
        self.build_knowledge_graph()
        descriptions = [self.kg.nodes[product.id]['description'] for product in self.products]
        self.X = self.vectorizer.fit_transform(descriptions)
        self.redis_client.set('recommendations_matrix', pickle.dumps(self.X))

    def recommend(self, product_id, num_recs=5):
        if self.redis_client.exists('recommendations_matrix'):
            self.X = pickle.loads(self.redis_client.get('recommendations_matrix'))
        else:
            self.fit()
        product_idx = self.products.filter(id=product_id).values_list('id', flat=True)[0] - 1
        product_vec = self.X[product_idx]
        similarities = cosine_similarity(self.X, product_vec).flatten()
        top_n = np.argsort(-similarities)[:num_recs + 1]  # Добавляем 1 для того, чтобы исключить сам продукт
        return [self.products[int(i)].id for i in top_n[1:]]

    def get_recommendations(self, product_id):
        recs = self.recommend(product_id)
        return [self.products.get(id=rec_id) for rec_id in recs]

    def visualize_graph(self):
        pos = nx.spring_layout(self.kg)
        nx.draw_networkx(self.kg, pos, with_labels=True, node_color='lightblue', edge_color='gray')

        # Save the graph to a buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Encode the graph to base64
        graph_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Return the HTML image tag
        return f'<img src="data:image/png;base64, {graph_base64}" alt="Recommendations Graph" />'
