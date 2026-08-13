import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    adjusted_rand_score
)
from typing import Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class MerinosClusteringEngine:
    """MERİNOS için kümeleme ve anomali tespiti motoru."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def fit_kmeans(self, X: np.ndarray, n_clusters: int = 4) -> Dict:
        """K-Means ile kümeleme yap ve metrikleri hesapla."""
        kmeans = KMeans(n_clusters=n_clusters,
                        random_state=self.random_state,
                        n_init=10)
        labels = kmeans.fit_predict(X)
        sil = silhouette_score(X, labels)
        dbi = davies_bouldin_score(X, labels)
        logger.info(f"K-Means tamamlandı. Silhouette: {sil:.4f}")
        return {"model": kmeans, "labels": labels,
                "silhouette_score": sil,
                "davies_bouldin_score": dbi}

    def fit_dbscan(self, X: np.ndarray, eps: float = 0.5,
                   min_samples: int = 5) -> Dict:
        """DBSCAN ile kümeleme yap."""
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        logger.info(f"DBSCAN tamamlandı. Küme sayısı: {n_clusters}")
        return {"model": dbscan, "labels": labels,
                "n_clusters": n_clusters}

    def detect_anomaly_sample(self, X: np.ndarray, sample: np.ndarray) -> float:
        """Verilen örneğin anomali olma olasılığını hesapla."""
        distances = np.linalg.norm(X - sample, axis=1)
        threshold = np.percentile(distances, 95)
        is_anomaly = float(distances.min() > threshold)
        return is_anomaly
