import numpy as np
from typing import List, Optional, Tuple, Set, Dict, Any
import faiss
import heapq
import math

from day26.mini_project.src.models import VectorPoint, SearchResult, PayloadFilter
from day26.mini_project.src.quantization import ScalarQuantizer


class HNSWVectorIndex:
    """
    HNSW (Hierarchical Navigable Small World) index
    for efficient approximate nearest neighbor search.
    """

    def __init__(
        self,
        dim: Optional[int] = None,
        m: int = 32,
        ef_construction: int = 200,
        ef_construct: Optional[int] = None,
        ef_search: int = 32,
        metric: str = "cosine",
        use_quantization: bool = False,
        M: Optional[int] = None,
        quantize: bool = False
    ):
        self.dim = dim
        self.m = M if M is not None else m
        self.ef_construction = ef_construct if ef_construct is not None else ef_construction
        self.ef_construct = self.ef_construction
        self.ef_search = ef_search
        self.metric = metric
        self.use_quantization = quantize or use_quantization
        self.index = None
        self.is_trained = False

        self.m0 = 2 * self.m
        self.m_l = 1.0 / math.log(max(self.m, 2))
        self.entry_point: Optional[int] = None
        self.max_level: int = -1

        self.points: List[VectorPoint] = []
        self.vectors: Optional[np.ndarray] = None
        self.graphs: List[Dict[int, Set[int]]] = []
        self.node_levels: Dict[int, int] = {}

        self.quantizer: Optional[ScalarQuantizer] = None
        self.quantized_vecs: Optional[np.ndarray] = None
        self.sq_scales: Optional[np.ndarray] = None
        self.sq_offsets: Optional[np.ndarray] = None

    @property
    def max_layer(self) -> int:
        return max(self.max_level, 0)

    def build(self, points: Any) -> "HNSWVectorIndex":
        """Alias for build_index."""
        return self.build_index(points)

    def _random_level(self) -> int:
        """Üstel dağılım ile düğümün atanacağı maksimum katmanı belirler."""
        u = np.random.uniform(1e-6, 1.0)
        return int(-math.log(u) * self.m_l)

    def _calc_dist(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Kosinüs mesafesi: 1.0 - Cosine Similarity (Küçük mesafe = Yüksek benzerlik)."""
        sim = float(np.dot(v1, v2))
        return 1.0 - sim

    def build_index(self, points: np.ndarray) -> "HNSWVectorIndex":
        """Build HNSW index from a set of vectors."""
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
        if self.dim is None:
            self.dim = d
        elif d != self.dim:
            raise ValueError(f"Dimension mismatch: expected {self.dim}, got {d}")

        print(f"[HNSW] Building index with m={self.m}, ef_construction={self.ef_construction}...")
        self.index = faiss.IndexHNSWFlat(self.dim, self.m)
        self.index.hnsw.efConstruction = self.ef_construction

        self.index.add(points.astype(np.float32))
        self.is_trained = True

        # Normalize et
        norms = np.linalg.norm(points, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.vectors = points / norms

        # Kuantizasyon gerekiyorsa hazırla
        if self.use_quantization:
            self.quantizer = ScalarQuantizer()
            self.quantizer.fit(self.vectors)
            self.quantized_vecs, self.sq_scales, self.sq_offsets = self.quantizer.quantize(self.vectors)

        self.graphs = []
        self.node_levels = {}
        self.entry_point = None
        self.max_level = -1

        for idx in range(len(self.points)):
            self._insert(idx)

        return self

    def _search_layer(self, query_vec: np.ndarray, enter_points: List[int], ef: int, level: int) -> List[Tuple[float, int]]:
        """Belirtilen katmanda en yakın ef adet komşuyu öncelik kuyruğu ile bulur."""
        visited: Set[int] = set(enter_points)
        candidates = []
        w = []

        for ep in enter_points:
            d = self._calc_dist(query_vec, self.vectors[ep])
            heapq.heappush(candidates, (d, ep))
            heapq.heappush(w, (-d, ep))

        while candidates:
            c_dist, c_idx = heapq.heappop(candidates)
            furthest_w_dist = -w[0][0]

            if c_dist > furthest_w_dist:
                break

            neighbors = self.graphs[level].get(c_idx, set())
            for n_idx in neighbors:
                if n_idx not in visited:
                    visited.add(n_idx)
                    furthest_w_dist = -w[0][0]
                    d_n = self._calc_dist(query_vec, self.vectors[n_idx])

                    if d_n < furthest_w_dist or len(w) < ef:
                        heapq.heappush(candidates, (d_n, n_idx))
                        heapq.heappush(w, (-d_n, n_idx))
                        if len(w) > ef:
                            heapq.heappop(w)

        return sorted([(-item[0], item[1]) for item in w], key=lambda x: x[0])

    def _insert(self, q_idx: int) -> None:
        """Yeni bir düğümü graf katmanlarına dinamik olarak bağlar."""
        q_vec = self.vectors[q_idx]
        level = self._random_level()
        self.node_levels[q_idx] = level

        while len(self.graphs) <= max(level, self.max_level):
            self.graphs.append({})

        if self.entry_point is None:
            self.entry_point = q_idx
            self.max_level = level
            for l in range(level + 1):
                self.graphs[l][q_idx] = set()
            return

        curr_obj = self.entry_point
        curr_dist = self._calc_dist(q_vec, self.vectors[curr_obj])

        for l in range(self.max_level, level, -1):
            changed = True
            while changed:
                changed = False
                neighbors = self.graphs[l].get(curr_obj, set())
                for n_idx in neighbors:
                    d = self._calc_dist(q_vec, self.vectors[n_idx])
                    if d < curr_dist:
                        curr_dist = d
                        curr_obj = n_idx
                        changed = True

        ep = [curr_obj]
        for l in range(min(level, self.max_level), -1, -1):
            w = self._search_layer(q_vec, ep, self.ef_construct, l)
            max_m = self.m0 if l == 0 else self.m

            selected_neighbors = [idx for dist, idx in w[:max_m]]
            self.graphs[l][q_idx] = set(selected_neighbors)

            for n_idx in selected_neighbors:
                self.graphs[l].setdefault(n_idx, set()).add(q_idx)
                if len(self.graphs[l][n_idx]) > max_m:
                    n_vec = self.vectors[n_idx]
                    sorted_nbrs = sorted(
                        list(self.graphs[l][n_idx]),
                        key=lambda x: self._calc_dist(n_vec, self.vectors[x])
                    )
                    self.graphs[l][n_idx] = set(sorted_nbrs[:max_m])

            ep = [idx for dist, idx in w]

        if level > self.max_level:
            self.max_level = level
            self.entry_point = q_idx

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        ef: Optional[int] = None,
        payload_filter: Optional[PayloadFilter] = None
    ) -> List[SearchResult]:
        """Graf üzerinden logaritmik rota takibi ile en yakın komşuları arar."""
        if self.entry_point is None or self.vectors is None:
            return []

        q_norm = query_vector.astype(np.float32)
        q_len = np.linalg.norm(q_norm)
        if q_len > 0:
            q_norm = q_norm / q_len

        search_ef = max(ef or self.ef_search, top_k)
        curr_obj = self.entry_point
        curr_dist = self._calc_dist(q_norm, self.vectors[curr_obj])

        for l in range(self.max_level, 0, -1):
            changed = True
            while changed:
                changed = False
                neighbors = self.graphs[l].get(curr_obj, set())
                for n_idx in neighbors:
                    d = self._calc_dist(q_norm, self.vectors[n_idx])
                    if d < curr_dist:
                        curr_dist = d
                        curr_obj = n_idx
                        changed = True

        w = self._search_layer(q_norm, [curr_obj], search_ef, 0)

        results = []
        rank = 1
        for dist, p_idx in w:
            pt = self.points[p_idx]
            if payload_filter is not None:
                if not payload_filter.evaluate(pt.payload):
                    continue

            sim_score = max(-1.0, min(1.0, 1.0 - dist))
            results.append(
                SearchResult(
                    point_id=pt.point_id,
                    score=float(sim_score),
                    payload=pt.payload,
                    content=pt.content,
                    rank=rank
                )
            )
            rank += 1
            if len(results) >= top_k:
                break

        return results

    def estimate_memory_bytes(self) -> int:
        """İndeksin RAM bellek ayak izini hesaplar."""
        if self.vectors is None:
            return 0
        if self.use_quantization and self.quantized_vecs is not None:
            vec_bytes = self.quantized_vecs.nbytes + (self.sq_scales.nbytes if self.sq_scales is not None else 0)
        else:
            vec_bytes = self.vectors.nbytes

        graph_bytes = 0
        for l_graph in self.graphs:
            for n_set in l_graph.values():
                graph_bytes += len(n_set) * 8
        return vec_bytes + graph_bytes
