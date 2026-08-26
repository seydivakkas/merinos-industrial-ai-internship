# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 32
Domain Models: Hybrid Retrieval, RRF Fusion, IR Evaluation Metrics, Diagnostic Error Taxonomy
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class GoldenQuery(BaseModel):
    """Altın kıyaslama veri setindeki tekil doğrulanmış test sorgusu."""
    model_config = ConfigDict(frozen=True)

    id: str = Field(description="Sorgu ID (örn: Q01_EXACT)")
    query: str = Field(description="Kullanıcı/operatör sorgu metni")
    category: str = Field(description="EXACT_CODE, SEMANTIC_SYMPTOM, HYBRID_COMPLEX, OUT_OF_DOMAIN")
    target_chunk_id: Optional[str] = Field(default=None, description="Hedef ground-truth parça kimliği")
    target_doc_id: Optional[str] = Field(default=None, description="Hedef ground-truth doküman kimliği")
    keywords: List[str] = Field(default_factory=list, description="Kritik anahtar kelimeler")
    description: str = Field(default="", description="Sorgunun endüstriyel bağlamı")


class FusedItem(BaseModel):
    """Hibrit arama (Lineer veya RRF) birleştirmesi sonrası tekil sıralı sonuç."""
    model_config = ConfigDict(frozen=True)

    chunk_id: str = Field(description="Parça kimliği")
    doc_id: str = Field(description="Doküman kimliği")
    final_score: float = Field(description="Birleştirilmiş hibrit benzerlik/sıralama skoru")
    rank: int = Field(description="Hibrit nihai sıralama derecesi (1, 2, ...)")
    bm25_rank: Optional[int] = Field(default=None, description="BM25 listesindeki sırası (varsa)")
    bm25_score: Optional[float] = Field(default=None, description="Ham BM25 skoru")
    dense_rank: Optional[int] = Field(default=None, description="Dense listesindeki sırası (varsa)")
    dense_score: Optional[float] = Field(default=None, description="Ham Cosine Sim skoru")
    source: str = Field(default="", description="Kaynak doküman adı")
    section: str = Field(default="", description="Bölüm başlığı")
    breadcrumbs: str = Field(default="", description="Hiyerarşik gezinme yolu")
    text_snippet: str = Field(default="", description="Metin önizlemesi (ilk 160 karakter)")


class HybridQueryResult(BaseModel):
    """Hibrit arama motoru çıktı kümesi."""
    model_config = ConfigDict(frozen=True)

    query: str = Field(description="Aranan sorgu")
    fusion_method: str = Field(description="linear veya rrf")
    alpha: Optional[float] = Field(default=None, description="Lineer ağırlık (alpha * BM25 + (1-alpha) * Dense)")
    k_rrf: Optional[int] = Field(default=None, description="RRF sabiti (varsayılan: 60)")
    items: List[FusedItem] = Field(default_factory=list, description="Top-K sıralı hibrit sonuçlar")
    latency_ms: float = Field(default=0.0, description="Birleştirme dahil toplam yanıt süresi (ms)")


class MetricScore(BaseModel):
    """Bir sistemin tüm bilgi getirme (IR) metriklerinin toplu sonucu."""
    model_config = ConfigDict(frozen=True)

    hit_at_k: Dict[int, float] = Field(default_factory=dict, description="Hit@1, Hit@3, Hit@5, Hit@10 başarı oranları")
    mrr: float = Field(default=0.0, description="Mean Reciprocal Rank (MRR)")
    precision_at_k: Dict[int, float] = Field(default_factory=dict, description="Precision@1, Precision@3, Precision@5")
    recall_at_k: Dict[int, float] = Field(default_factory=dict, description="Recall@1, Recall@3, Recall@5")
    ndcg_at_k: Dict[int, float] = Field(default_factory=dict, description="NDCG@1, NDCG@3, NDCG@5, NDCG@10")


class QueryEvaluationResult(BaseModel):
    """Tek bir sorgunun tek bir retrieval motorundaki detaylı değerlendirme çıktısı."""
    model_config = ConfigDict(frozen=True)

    query_id: str
    query: str
    category: str
    target_chunk_id: Optional[str]
    target_doc_id: Optional[str]
    found_rank: Optional[int] = Field(default=None, description="Hedef chunk'ın bulunduğu sıra (yoksa None)")
    hit_at_k: Dict[int, bool] = Field(default_factory=dict)
    reciprocal_rank: float = Field(default=0.0)
    top1_retrieved_chunk_id: Optional[str] = None
    top1_correct: bool = False


class SystemEvaluationReport(BaseModel):
    """Bir arama sisteminin (BM25, Dense, Linear, RRF) tam değerlendirme raporu."""
    model_config = ConfigDict(frozen=True)

    system_name: str = Field(description="BM25, Dense, Linear_0.5, RRF_k60 vb.")
    overall_metrics: MetricScore
    category_breakdown: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Kategori bazlı (EXACT, SEMANTIC, HYBRID) Hit@1, Hit@3, MRR dağılımı"
    )
    total_queries: int
    valid_queries: int
    results: List[QueryEvaluationResult] = Field(default_factory=list)


class AlphaSweepPoint(BaseModel):
    """Lineer birleştirme parametresi alpha için duyarlılık analiz noktası."""
    model_config = ConfigDict(frozen=True)

    alpha: float
    hit_at_1: float
    hit_at_3: float
    hit_at_5: float
    mrr: float
    ndcg_at_5: float


class ErrorRecord(BaseModel):
    """Değerlendirmede başarısız olan sorguların kök neden analiz kaydı."""
    model_config = ConfigDict(frozen=True)

    query_id: str
    query: str
    category: str
    system_name: str
    failure_type: str = Field(description="KEYWORD_MISMATCH, CODE_DRIFT, CHUNK_BOUNDARY, OUT_OF_DOMAIN")
    expected_target: Optional[str]
    actual_top1: Optional[str]
    target_rank: Optional[int]
    explanation: str
    recommendation: str


class ComprehensiveBenchmarkReport(BaseModel):
    """Tüm sistemleri karşılaştıran konsolide kıyaslama ve değerlendirme raporu."""
    model_config = ConfigDict(frozen=True)

    generated_at: str
    systems: Dict[str, SystemEvaluationReport]
    alpha_sweep: List[AlphaSweepPoint]
    error_records: List[ErrorRecord]
    best_system_mrr: str
    best_system_hit1: str
    best_alpha: float
    executive_summary: str
