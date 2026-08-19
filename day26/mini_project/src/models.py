"""
Merinos Industrial AI Internship - Day 26
Vector Indexing & Optimization Data Models (Pydantic v2)

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, computed_field


class VectorPoint(BaseModel):
    """Vektör veritabanına eklenecek birincil nokta ve metadata modeli."""
    point_id: Union[int, str] = Field(description="Tekil nokta ID'si")
    chunk_id: str = Field(description="Ait olduğu parça ID'si")
    doc_id: str = Field(description="Ait olduğu doküman ID'si")
    title: str = Field(description="Doküman başlığı")
    breadcrumbs: str = Field(default="", description="Hiyerarşik başlık yolu")
    content: str = Field(description="Metin içeriği")
    machine: str = Field(description="İlişkili makine modeli")
    department: str = Field(description="Departman/proses kategorisi")
    component: str = Field(default="", description="Spesifik makine bileşeni")
    priority: str = Field(default="NORMAL", description="Kritiklik seviyesi (CRITICAL, HIGH, MEDIUM, NORMAL)")
    char_length: int = Field(default=0, description="Karakter uzunluğu")
    token_count: int = Field(default=0, description="Kelime/token sayısı")
    vector: List[float] = Field(description="Yoğun gömme vektörü (384-boyutlu)")

    @computed_field
    @property
    def payload(self) -> Dict[str, Any]:
        """Qdrant ve filtreleme için birleşik payload sözlüğü."""
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "title": self.title,
            "breadcrumbs": self.breadcrumbs,
            "machine": self.machine,
            "department": self.department,
            "component": self.component,
            "priority": self.priority,
            "char_length": self.char_length,
            "token_count": self.token_count
        }


class FilterCondition(BaseModel):
    """Tekil bir metadata filtre koşulu."""
    key: str = Field(default="", description="Filtrelenecek payload alanı (örn: department)")
    field: Optional[str] = None
    operator: str = "eq"
    value: Optional[Any] = None
    match_value: Optional[Any] = Field(default=None, description="Tam eşleşme değeri")
    range_gte: Optional[float] = Field(default=None, description="Sayısal alt sınır (>=)")
    range_lte: Optional[float] = Field(default=None, description="Sayısal üst sınır (<=)")

    def model_post_init(self, __context: Any) -> None:
        if self.field and not self.key:
            self.key = self.field
        if self.value is not None and self.match_value is None:
            self.match_value = self.value

    def matches(self, payload: Dict[str, Any]) -> bool:
        """Verilen payload'un bu koşulu sağlayıp sağlamadığını denetler."""
        target_key = self.key or self.field or ""
        if target_key not in payload:
            return False
        val = payload[target_key]
        match_val = self.match_value if self.match_value is not None else self.value
        if match_val is not None:
            if isinstance(match_val, list):
                if val not in match_val:
                    return False
            else:
                s_val = str(val).lower()
                s_match = str(match_val).lower()
                if s_val != s_match:
                    val_tokens = set(s_val.replace("-", "_").split("_"))
                    match_tokens = set(s_match.replace("-", "_").split("_"))
                    if not (val_tokens & match_tokens):
                        return False
        if self.range_gte is not None:
            if float(val) < self.range_gte:
                return False
        if self.range_lte is not None:
            if float(val) > self.range_lte:
                return False
        return True


class PayloadFilter(BaseModel):
    """Çoklu koşullu birleşik metadata filtresi."""
    must: List[FilterCondition] = Field(default_factory=list, description="Tüm koşulların sağlanması gerekir (AND)")
    should: List[FilterCondition] = Field(default_factory=list, description="En az bir koşulun sağlanması gerekir (OR)")
    must_not: List[FilterCondition] = Field(default_factory=list, description="Hiçbir koşulun sağlanmaması gerekir (NOT)")
    conditions: Optional[List[FilterCondition]] = None

    def model_post_init(self, __context: Any) -> None:
        if self.conditions:
            self.must.extend(self.conditions)

    def evaluate(self, payload: Dict[str, Any]) -> bool:
        """Payload'un filtre kümesini geçerli kılıp kılmadığını hesaplar."""
        for cond in self.must:
            if not cond.matches(payload):
                return False
        if self.should:
            if not any(cond.matches(payload) for cond in self.should):
                return False
        for cond in self.must_not:
            if cond.matches(payload):
                return False
        return True

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PayloadFilter":
        """Sözlükten basit must filtresi üretir (örn: {'department': 'DOKUMA_TEZGAHI_BAKIM'})."""
        conditions = []
        for k, v in d.items():
            conditions.append(FilterCondition(key=k, match_value=v))
        return cls(must=conditions)


class SearchResult(BaseModel):
    """Vektör arama sonuç maddesi."""
    point_id: Union[int, str]
    score: float = Field(description="Benzerlik skoru (Kosinüs: 0.0 - 1.0)")
    payload: Dict[str, Any]
    content: str = ""
    rank: int = 1

    @property
    def doc_id(self) -> str:
        return self.payload.get("doc_id", str(self.point_id))


class IndexBenchmarkMetrics(BaseModel):
    """Bir indeks konfigürasyonunun performans ve kaynak tüketim metrikleri."""
    index_type: str = Field(description="İndeks türü (flat, ivf, hnsw, quantized_hnsw)")
    total_vectors: int
    dimension: int
    indexing_time_ms: float = Field(description="Tüm korpusu indeksleme süresi (ms)")
    query_latency_ms: float = Field(description="Ortalama sorgu süresi (ms)")
    qps: float = Field(description="Saniyedeki sorgu kapasitesi (Queries Per Second)")
    memory_bytes: int = Field(description="Tahmini RAM bellek tüketimi (Byte)")
    memory_kb: float = Field(description="RAM bellek tüketimi (KB)")
    recall_at_5: float = Field(description="Exact Flat aramaya göre Recall@5 doğruluğu")
    precision_at_1: float = Field(description="Precision@1 doğruluğu")
    ndcg_at_5: float = Field(description="NDCG@5 sıralama kalitesi")
    filtered_recall_at_5: float = Field(default=1.0, description="Filtreli aramadaki Recall@5")

    @property
    def build_time_ms(self) -> float:
        return self.indexing_time_ms

    @property
    def avg_latency_ms(self) -> float:
        return self.query_latency_ms

    @property
    def recall_at_k(self) -> float:
        return self.recall_at_5

    @property
    def filtered_recall_at_k(self) -> float:
        return self.filtered_recall_at_5


class VectorIndexReport(BaseModel):
    """Tüm indeks mimarilerinin büyük kıyaslama raporu."""
    indices: Dict[str, IndexBenchmarkMetrics]
    total_vectors: int
    dimension: int
    total_queries: int
    best_qps_index: str
    best_recall_index: str
    most_memory_efficient_index: str
    config_summary: Dict[str, Any]

    @property
    def metrics(self) -> List[IndexBenchmarkMetrics]:
        return list(self.indices.values())

    @property
    def fastest_index(self) -> str:
        return self.best_qps_index

    @property
    def most_accurate_index(self) -> str:
        return self.best_recall_index

    @property
    def most_memory_efficient(self) -> str:
        return self.most_memory_efficient_index

