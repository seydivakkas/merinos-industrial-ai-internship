import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models

from day23.mini_project.src.models import RawDocument, DenseSearchResultItem

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Qdrant üzerinde doküman vektörlerini saklayan vektör veritabanı arayüzü."""

    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "merinos_technical_docs",
        vector_size: int = 384,
        distance: models.Distance = models.Distance.COSINE,
        in_memory: Optional[bool] = None,
        path: Optional[str] = None,
    ):
        self.url = url
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance

        if in_memory or url == ":memory:":
            self.client = QdrantClient(":memory:")
        else:
            try:
                self.client = QdrantClient(url=url, timeout=1.0)
                # Bağlantı testi
                self.client.get_collections()
            except Exception:
                logger.info("Qdrant servisine bağlanılamadı, :memory: moduna geçiliyor.")
                self.client = QdrantClient(":memory:")

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            logger.info(f"Qdrant koleksiyonu oluşturuluyor: {self.collection_name}")
            try:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=self.distance,
                    ),
                )
            except Exception:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=self.distance,
                    ),
                )

    def init_collection(self) -> None:
        """Koleksiyonu sıfırdan oluşturur veya mevcut olanı kontrol eder."""
        self._ensure_collection()

    def upsert_documents(
        self,
        documents: List[Union[Dict[str, Any], RawDocument]],
        vectors: np.ndarray,
    ) -> int:
        """Dokümanları ve vektörlerini Qdrant'a ekler (upsert)."""
        assert len(documents) == len(vectors), "Doküman ve vektör sayısı uyuşmuyor."
        points = []
        for idx, (doc, vec) in enumerate(zip(documents, vectors)):
            if isinstance(doc, dict):
                doc_id = doc.get("doc_id", doc.get("id", f"DOC-{idx+1}"))
                title = doc.get("title", "")
                category = doc.get("category", "UNKNOWN")
                tags = doc.get("tags", [])
                content = doc.get("content", "")
                snippet = doc.get("snippet", " ".join(content.split())[:160] + "...")
            else:
                doc_id = getattr(doc, "doc_id", f"DOC-{idx+1}")
                title = getattr(doc, "title", "")
                category = getattr(doc, "category", "UNKNOWN")
                tags = getattr(doc, "tags", [])
                content = getattr(doc, "content", "")
                snippet = " ".join(content.split())[:160] + "..."

            payload = {
                "doc_id": doc_id,
                "title": title,
                "category": category,
                "tags": tags,
                "snippet": snippet,
            }
            points.append(
                models.PointStruct(
                    id=idx + 1,
                    vector=vec.tolist() if isinstance(vec, np.ndarray) else vec,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        return len(points)

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        category_filter: Optional[str] = None,
    ) -> List[DenseSearchResultItem]:
        """Qdrant üzerinde vektör araması gerçekleştirir ve opsiyonel filtre uygular."""
        query_list = query_vector.flatten().tolist()

        search_filter = None
        if category_filter:
            search_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="category",
                        match=models.MatchValue(value=category_filter.upper()),
                    )
                ]
            )

        try:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_list,
                query_filter=search_filter,
                limit=top_k,
            )
        except AttributeError:
            res = self.client.query_points(
                collection_name=self.collection_name,
                query=query_list,
                query_filter=search_filter,
                limit=top_k,
            )
            hits = res.points

        results: List[DenseSearchResultItem] = []
        for rank, hit in enumerate(hits, start=1):
            payload = hit.payload or {}
            results.append(
                DenseSearchResultItem(
                    doc_id=payload.get("doc_id", f"DOC-{hit.id}"),
                    title=payload.get("title", ""),
                    score=float(hit.score),
                    rank=rank,
                    snippet=payload.get("snippet", ""),
                    category=payload.get("category", "UNKNOWN"),
                    tags=payload.get("tags", []),
                )
            )

        return results

    def count(self) -> int:
        """Koleksiyondaki toplam vektör sayısını döndürür."""
        info = self.client.get_collection(self.collection_name)
        return info.points_count or 0
