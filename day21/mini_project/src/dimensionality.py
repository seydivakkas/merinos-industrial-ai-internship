import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MerinosDimensionalityReducer:
    """MERİNOS için boyut indirgeme araçları
    (PCA, t-SNE)."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def fit_pca(self, X: np.ndarray,
                n_components: int = 0.95) -> Tuple[PCA, np.ndarray]:
        """PCA uygula ve açıklanan varyans oranını döndür."""
        pca = PCA(n_components=n_components,
                  random_state=self.random_state)
        X_pca = pca.fit_transform(X)
        explained_variance_ratio = pca.explained_variance_ratio_
        logger.info(f"PCA tamamlandı. Bileşen sayısı: {pca.n_components_}")
        return pca, X_pca, explained_variance_ratio

    def fit_tsne(self, X: np.ndarray,
                 n_components: int = 2,
                 perplexity: int = 30,
                 random_state: Optional[int] = None) -> np.ndarray:
        """t-SNE ile 2D/3D boyut indirgeme uygula."""
        tsne = TSNE(n_components=n_components,
                    perplexity=perplexity,
                    random_state=random_state or self.random_state,
                    init='pca',
                    learning_rate='auto')

        X_tsne = tsne.fit_transform(X)
        logger.info(f"t-SNE tamamlandı. Şekil: {X_tsne.shape}")
        return X_tsne
