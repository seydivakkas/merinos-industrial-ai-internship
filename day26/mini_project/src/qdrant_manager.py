"""
Merinos Industrial AI Internship - Day 26
Production Qdrant Vector Store with HNSW & Scalar Quantization

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional, Union
import numpy as np
from qdrant_client import QdrantClient
import qdrant_client.models as qm

from day26.mini_project.src.models import VectorPoint, SearchResult, PayloadFilter


class QdrantVectorStore:
    """
    Qdrant vektör veritabanı motoru:
    HNSW graf indeksleme, Int8 Skaler Kuantizasyon ve yapılandırılmış
    payload filtreleme (Pre-filtering) yeteneklerini endüstriyel standartta sunar.
    """

    def __init__(
        self,
        collection_name: str = "merinos_maintenance_vectors",
        dimension: int = 384,
        url: Optional[str] = None,
        prefer_grpc: bool = False,
        vector_size: Optional[int] = None,
        in_memory: bool = True
    ):
        self.collection_name = collection_name
        self.dimension = vector_size if vector_size is not None else dimension

        # Eğer url verilmemişse %100 yerel ve deterministik in-memory istemci başlat
        if url:
            self.client = QdrantClient(url=url, prefer_grpc=prefer_grpc)
        else:
            self.client = QdrantClient(":memory:")

    def get_collection_info(self) -> Any:
        """Koleksiyon bilgilerini döner."""
        return self.client.get_collection(self.collection_name)

    def create_collection(
        self,
        m: int = 16,
        ef_construct: int = 64,
        use_quantization: bool = False,
        full_scan_threshold: int = 1000,
        enable_quantization: bool = False
    ) -> None:
        """Koleksiyonu belirtilen HNSW ve Kuantizasyon parametreleriyle oluşturur."""
        use_quant = enable_quantization or use_quantization
        # Varsa eskiyi temizle
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if exists:
            self.client.delete_collection(self.collection_name)

        hnsw_diff = qm.HnswConfigDiff(
            m=m,
            ef_construct=ef_construct,
            full_scan_threshold=full_scan_threshold
        )

        quant_config = None
        if use_quant:
            quant_config = qm.ScalarQuantization(
                scalar=qm.ScalarQuantizationConfig(
                    type=qm.ScalarType.INT8,
                    quantile=0.99,
                    always_ram=True
                )
            )

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qm.VectorParams(
                size=self.dimension,
                distance=qm.Distance.COSINE
            ),
            hnsw_config=hnsw_diff,
            quantization_config=quant_config
        )

    def create_payload_index(self, field_name: str, field_type: str = "keyword") -> None:
        """Hızlı filtreleme için payload alanlarına indeks tanımlar."""
        schema = qm.PayloadSchemaType.KEYWORD if field_type == "keyword" else qm.PayloadSchemaType.INTEGER
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name=field_name,
            field_schema=schema
        )

    def upsert_points(self, points: List[VectorPoint], batch_size: int = 64) -> int:
        """Noktaları toplu (batch) olarak koleksiyona yazar."""
        if not points:
            return 0

        total = len(points)
        for i in range(0, total, batch_size):
            batch = points[i:i + batch_size]
            qdrant_points = []
            for p in batch:
                # ID sayısal veya str olabilir
                pid = int(p.point_id) if str(p.point_id).isdigit() else str(p.point_id)
                qdrant_points.append(
                    qm.PointStruct(
                        id=pid,
                        vector=p.vector,
                        payload=p.payload
                    )
                )
            self.client.upsert(
                collection_name=self.collection_name,
                points=qdrant_points
            )

        return total

    def _convert_filter(self, payload_filter: PayloadFilter) -> qm.Filter:
        """Bizim PayloadFilter nesnemizi Qdrant qm.Filter formatına dönüştürür."""
        must_conditions = []
        for cond in payload_filter.must:
            if cond.match_value is not None:
                must_conditions.append(
                    qm.FieldCondition(
                        key=cond.key,
                        match=qm.MatchValue(value=cond.match_value)
                    )
                )
            if cond.range_gte is not None or cond.range_lte is not None:
                must_conditions.append(
                    qm.FieldCondition(
                        key=cond.key,
                        range=qm.Range(gte=cond.range_gte, lte=cond.range_lte)
                    )
                )

        should_conditions = []
        for cond in payload_filter.should:
            if cond.match_value is not None:
                should_conditions.append(
                    qm.FieldCondition(
                        key=cond.key,
                        match=qm.MatchValue(value=cond.match_value)
                    )
                )

        must_not_conditions = []
        for cond in payload_filter.must_not:
            if cond.match_value is not None:
                must_not_conditions.append(
                    qm.FieldCondition(
                        key=cond.key,
                        match=qm.MatchValue(value=cond.match_value)
                    )
                )

        return qm.Filter(
            must=must_conditions or None,
            should=should_conditions or None,
            must_not=must_not_conditions or None
        )

    def search(
        self,
        query_vector: Union[List[float], np.ndarray],
        top_k: int = 5,
        payload_filter: Optional[PayloadFilter] = None,
        exact: bool = False
    ) -> List[SearchResult]:
        """Qdrant query_points API'sini kullanarak filtrelenmiş vektör araması yapar."""
        vec = query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector
        q_filter = self._convert_filter(payload_filter) if payload_filter else None

        search_params = qm.SearchParams(exact=exact) if exact else None

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=vec,
            query_filter=q_filter,
            search_params=search_params,
            limit=top_k,
            with_payload=True
        )

        results = []
        for rank, p in enumerate(response.points, start=1):
            results.append(
                SearchResult(
                    point_id=p.id,
                    score=float(p.score),
                    payload=p.payload or {},
                    content=str((p.payload or {}).get("breadcrumbs", "")),
                    rank=rank
                )
            )

        return results

    def count_points(self) -> int:
        """Koleksiyondaki toplam nokta sayısını döner."""
        info = self.client.get_collection(self.collection_name)
        return info.points_count or 0
