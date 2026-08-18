"""
Merinos Industrial AI Internship - Day 25
Document Chunking Data Models (Pydantic v2)

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, computed_field


class DocumentItem(BaseModel):
    """Kurumsal teknik SOP ve bakım dokümanı veri modeli."""
    doc_id: str = Field(description="Tekil doküman tanımlayıcısı (örn: SOP-001)")
    title: str = Field(description="Doküman başlığı")
    category: str = Field(description="Departman/proses kategorisi")
    content: str = Field(description="Tüm dokümanın ham metin içeriği")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Ek makine ve revizyon bilgisi")

    def get(self, key: str, default: Any = None) -> Any:
        """Sözlük arayüzü uyumluluğu için get metodu."""
        if key == "id":
            return getattr(self, "doc_id", default)
        return getattr(self, key, default)


class ChunkItem(BaseModel):
    """Parçalanmış metin bloğu ve bağlamsal metadata modeli."""
    chunk_id: str = Field(description="Tekil parça ID'si (örn: SOP-001_chunk_001)")
    doc_id: str = Field(description="Ait olduğu ana doküman ID'si")
    title: str = Field(description="Ana doküman başlığı")
    category: str = Field(description="Doküman kategorisi")
    content: str = Field(description="Parça metni")
    strategy: str = Field(description="Kullanılan parçalama stratejisi")
    chunk_index: int = Field(description="Doküman içindeki parça sırası (1-tabanlı)")
    total_chunks_in_doc: int = Field(default=1, description="Dokümanın toplam parça sayısı")
    char_start: int = Field(default=0, description="Orijinal dokümandaki başlangıç karakter konumu")
    char_end: int = Field(default=0, description="Orijinal dokümandaki bitiş karakter konumu")
    char_length: int = Field(default=0, description="Parçanın karakter uzunluğu")
    token_count: int = Field(default=0, description="Tahmini token veya kelime sayısı")
    section_headers: List[str] = Field(default_factory=list, description="Hiyerarşik başlık yolu (breadcrumbs)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Ek bağlamsal metadata")

    @computed_field
    @property
    def breadcrumb_str(self) -> str:
        """Hiyerarşik başlık yolunun okunabilir metin formatı."""
        return " > ".join(self.section_headers) if self.section_headers else self.title


class ChunkingStats(BaseModel):
    """Bir parçalama stratejisinin geometrik ve anlamsal istatistikleri."""
    strategy: str
    total_chunks: int
    mean_char_length: float
    median_char_length: float
    min_char_length: int
    max_char_length: int
    std_char_length: float
    mean_token_count: float
    intra_chunk_coherence: float = Field(description="Parça içi ardışık cümlelerin kosinüs benzerliği")
    breadcrumb_coverage_ratio: float = Field(description="Başlık yolu korunan parçaların oranı (0.0-1.0)")
    redundancy_ratio: float = Field(description="Örtüşme nedeniyle toplam karakter artış oranı (>= 1.0)")


class RetrievalMetrics(BaseModel):
    """Parçaların bilgi getirme (Retrieval) başarımı."""
    precision_at_1: float
    recall_at_5: float
    mrr: float
    ndcg_at_5: float
    needle_hit_rate_at_1: float = Field(description="Hedef cümlenin 1. parçada bulunma oranı")
    needle_hit_rate_at_5: float = Field(description="Hedef cümlenin ilk 5 parçada bulunma oranı")


class StrategyEvaluationResult(BaseModel):
    """Bir stratejinin tüm boyutlardaki değerlendirme çıktısı."""
    strategy_name: str
    stats: ChunkingStats
    retrieval: RetrievalMetrics
    indexing_latency_ms: float
    query_latency_ms: float


class ChunkingBenchmarkReport(BaseModel):
    """4 parçalama stratejisinin büyük kıyaslama raporu."""
    strategies: Dict[str, StrategyEvaluationResult]
    total_documents: int
    total_queries: int
    best_retrieval_strategy: str
    best_coherence_strategy: str
    config_summary: Dict[str, Any]
