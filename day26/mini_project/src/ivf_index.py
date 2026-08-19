import numpy as np
from typing import List, Tuple, Optional, Any, Dict
from sklearn.cluster import KMeans
import faiss

from day26.mini_project.src.models import VectorPoint, SearchResult, PayloadFilter


class InvertedFileIndex:
    """
    Inverted File (IVF) index using centroid-based clustering
    for efficient vector search.
    """

    def __init__(
        self,
        nlist: int = 100,
        dim: Optional[int] = None,
        nprobe: int = 3,
        metric: str = "cosine",
        random_state: int = 42
    ):
        self.nlist = nlist
        self.dim = dim
        self.quantizer = None
        self.index = None
        self.is_trained = False
        self.random_state = random_state

        self.nprobe = nprobe
        self.metric = metric
        self.centroids: Optional[np.ndarray] = None
        self.inverted_lists: Dict[int, List[int]] = {}
        self.points: List[VectorPoint] = []
        self.vector_matrix: Optional[np.ndarray] = None
        self.is_built: bool = False

    def build(self, points: Any) -> "InvertedFileIndex":
        """Alias for build_index."""
        return self.build_index(points)

    def build_index(self, points: np.ndarray) -> "InvertedFileIndex":
        """Build IVF index from a set of vectors."""
        if not isinstance(points, np.ndarray) and hasattr(points, "__iter__"):
            if len(points) > 0 and hasattr(points[0], "vector"):
                self.points = list(points)
                points = np.array([p.vector for p in points], dtype=np.float32)
            else:
                points = np.asarray(points, dtype=np.float32)
        elif isinstance(points, np.ndarray) and not self.points:
            self.points = [
                VectorPoint(
                    point_id=i,
                    chunk_id=f"chk_{i:03d}",
                    doc_id=f"SOP-{i:03d}",
                    title=f"Vektör Noktası {i}",
                    breadcrumbs=f"Endüstriyel Vektör > {i}",
                    content=f"İndekslenen vektör noktası {i}",
                    machine="Genel",
                    department="GENEL",
                    component="Motor",
                    priority="NORMAL",
                    char_length=0,
                    token_count=0,
                    vector=points[i].tolist()
                )
                for i in range(len(points))
            ]

        if points.ndim != 2:
            raise ValueError("Points must be a 2D array")
        n, d = points.shape
        self.dim = d

        # create quantizer using k-means
        print(f"[IVF] Training k-means with {self.nlist} ce...")
        k = min(self.nlist, n)
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(points)
        centroids = kmeans.cluster_centers_.astype(np.float32)

        self.quantizer = faiss.IndexFlatL2(d)
        self.quantizer.add(centroids)

        # Normalize et (Kosinüs için birim vektör)
        norms = np.linalg.norm(points, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.vector_matrix = points / norms

        c_norms = np.linalg.norm(centroids, axis=1, keepdims=True)
        c_norms[c_norms == 0] = 1.0
        self.centroids = centroids / c_norms

        # Ters dizin listelerini oluştur
        cluster_labels = kmeans.labels_
        self.inverted_lists = {i: [] for i in range(k)}
        for p_idx, c_label in enumerate(cluster_labels):
            self.inverted_lists[c_label].append(p_idx)

        self.is_trained = True
        self.is_built = True
        return self

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        nprobe: Optional[int] = None,
        payload_filter: Optional[PayloadFilter] = None
    ) -> List[SearchResult]:
        """
        En yakın nprobe centroid hücresini belirler, adayları toplar
        ve opsiyonel ön-filtreleme (pre-filtering) uygulayarak top-k sonucu döner.
        """
        if not self.is_built or self.centroids is None or self.vector_matrix is None:
            raise RuntimeError("İndeks henüz oluşturulmadı (build_index çağrılmalı).")

        probe_count = min(nprobe or self.nprobe, len(self.centroids))

        # 1. Sorgu vektörünü normalize et
        q_norm = query_vector.astype(np.float32)
        q_len = np.linalg.norm(q_norm)
        if q_len > 0:
            q_norm = q_norm / q_len

        # 2. En yakın centroidleri tespit et (Kosinüs benzerliği)
        centroid_sims = np.dot(self.centroids, q_norm)
        best_centroids = np.argsort(-centroid_sims)[:probe_count]

        # 3. Aday havuzunu topla
        candidate_indices = []
        for c_id in best_centroids:
            candidate_indices.extend(self.inverted_lists[c_id])

        if not candidate_indices:
            # Fallback: tüm noktaları aday yap
            candidate_indices = list(range(len(self.points)))

        # 4. Ön-filtreleme (Pre-filtering): Filtreyi sağlamayanları ele
        if payload_filter is not None:
            valid_candidates = []
            for idx in candidate_indices:
                if payload_filter.evaluate(self.points[idx].payload):
                    valid_candidates.append(idx)
            candidate_indices = valid_candidates

        if not candidate_indices:
            return []

        # 5. Aday vektörlerle kosinüs benzerliği hesapla
        cand_vecs = self.vector_matrix[candidate_indices]
        scores = np.dot(cand_vecs, q_norm)

        # 6. Sırala ve top-k oluştur
        sorted_pos = np.argsort(-scores)[:top_k]
        results = []
        for rank, pos in enumerate(sorted_pos, start=1):
            p_idx = candidate_indices[pos]
            pt = self.points[p_idx]
            results.append(
                SearchResult(
                    point_id=pt.point_id,
                    score=float(scores[pos]),
                    payload=pt.payload,
                    content=pt.content,
                    rank=rank
                )
            )

        return results

    def estimate_memory_bytes(self) -> int:
        """İndeksin RAM üzerindeki tahmini bayt boyutunu döner."""
        if not self.is_built or self.vector_matrix is None:
            return 0
        vec_bytes = self.vector_matrix.nbytes
        centroids_bytes = self.centroids.nbytes if self.centroids is not None else 0
        inv_list_bytes = sum(len(lst) * 8 for lst in self.inverted_lists.values())
        return vec_bytes + centroids_bytes + inv_list_bytes
