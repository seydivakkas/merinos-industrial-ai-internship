# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 31
Domain Models: Raw Document, Chunk Record, Retrieval Item, Comparison Result
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict


class RawDocument(BaseModel):
    """Fiziksel PDF, Word, Markdown veya Metin dosyasından ayıklanan ham belge."""
    model_config = ConfigDict(frozen=True)

    doc_id: str = Field(description="Benzersiz doküman kimliği (örn: DOC_WEAVING_SOP)")
    filename: str = Field(description="Dosya adı (örn: merinos_weaving_sop.pdf)")
    file_type: str = Field(description="Dosya uzantısı / türü (pdf, docx, md, txt)")
    file_hash: str = Field(description="SHA-256 dosya içerik özeti")
    title: str = Field(description="Doküman başlığı")
    pages: List[Tuple[int, str]] = Field(
        default_factory=list,
        description="Sayfa no ve sayfa ham metni çiftleri listesi: [(1, 'sayfa 1 metni'), ...]"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Doküman seviyesi ek meta veriler (kategori, yazar, versiyon, tarih)"
    )
    total_char_count: int = Field(default=0, description="Tüm sayfalardaki toplam karakter sayısı")


class ChunkRecord(BaseModel):
    """Metin parçalama (chunking) sonrası elde edilen ve indekslenen birim parça."""
    model_config = ConfigDict(frozen=True)

    chunk_id: str = Field(description="Benzersiz parça kimliği (örn: DOC_WEAVING_SOP_c001)")
    doc_id: str = Field(description="Bağlı olduğu ham doküman kimliği")
    title: str = Field(description="Bağlı olduğu doküman başlığı")
    source: str = Field(description="Kaynak dosya yolu veya adı")
    page_number: int = Field(default=1, description="Parçanın başladığı sayfa numarası")
    section: str = Field(default="Genel", description="Bölüm veya başlık adı")
    breadcrumbs: str = Field(
        default="",
        description="Hiyerarşik gezinme yolu (örn: 'Merinos Halı > Dokuma SOP > Bölüm 2: Tarak Ayarları')"
    )
    text: str = Field(description="Parçanın temizlenmiş metin içeriği")
    char_count: int = Field(description="Parça karakter uzunluğu")
    token_estimate: int = Field(description="Yaklaşık token sayısı (~char / 4)")
    chunk_strategy: str = Field(default="fixed", description="fixed veya semantic")


class RetrievalItem(BaseModel):
    """Arama motorundan (BM25 veya Dense) dönen tekil aday sonuç."""
    model_config = ConfigDict(frozen=True)

    chunk_id: str = Field(description="Bulunan parçanın kimliği")
    doc_id: str = Field(description="Bulunan parçanın doküman kimliği")
    score: float = Field(description="Algoritmik benzerlik skoru (BM25 skoru veya Cosine Sim)")
    rank: int = Field(description="Sonuç listesindeki sıra numarası (1, 2, ...)")
    source: str = Field(description="Kaynak dosya adı")
    page_number: int = Field(description="Sayfa numarası")
    section: str = Field(description="Bölüm adı")
    breadcrumbs: str = Field(description="Hiyerarşik yol")
    text_snippet: str = Field(description="Metin önizlemesi (ilk 160 karakter)")


class QueryResult(BaseModel):
    """Bir sorgunun getirme (retrieval) sonuç kümesi."""
    model_config = ConfigDict(frozen=True)

    query: str = Field(description="Kullanıcı sorgusu")
    query_type: str = Field(description="exact veya semantic")
    method: str = Field(description="bm25 veya dense")
    items: List[RetrievalItem] = Field(default_factory=list, description="Top-K sıralı adaylar")
    latency_ms: float = Field(default=0.0, description="Arama süresi (milisaniye)")


class ComparisonResult(BaseModel):
    """Aynı sorgu için BM25 ve Dense arama davranışlarının karşılaştırma raporu."""
    model_config = ConfigDict(frozen=True)

    query: str = Field(description="Test sorgusu")
    query_type: str = Field(description="exact veya semantic")
    expected_doc_id: Optional[str] = Field(default=None, description="Beklenen hedef doküman ID'si")
    bm25_top1_id: str = Field(description="BM25'in 1. sıradaki chunk ID'si")
    bm25_top1_score: float = Field(description="BM25 1. sıra skoru")
    dense_top1_id: str = Field(description="Dense'in 1. sıradaki chunk ID'si")
    dense_top1_score: float = Field(description="Dense 1. sıra skoru")
    rank_alignment: bool = Field(description="İki motorun 1. sıradaki tercihi aynı mı?")
    winner_method: str = Field(description="bm25, dense veya tie")
    rationale: str = Field(description="Davranış farkının teknik gerekçesi")


class IndexManifest(BaseModel):
    """Tüm indekslenen belgelerin hash ve durum manifestosu (Auto-Sync omurgası)."""
    indexed_at: str = Field(description="Son indeksleme ISO zaman damgası")
    total_documents: int = Field(default=0)
    total_chunks: int = Field(default=0)
    documents: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="filename -> {doc_id, file_hash, file_type, chunk_count, pages_count}"
    )
