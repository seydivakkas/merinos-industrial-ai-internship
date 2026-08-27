# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 33
Domain Models: RAG Context, Source IDs, Attributed Answers, Citation Verification & Error Classification
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class SourceChunk(BaseModel):
    """Context içine dahil edilen ve [S1], [S2] şeklinde etiketlenen kaynak parça."""
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(description="Kaynak referans etiketi (örn: 'S1', 'S2')")
    chunk_id: str = Field(description="Özgün parça kimliği (örn: 'DOC_MERINOS_WEAVING_SOP_c004')")
    doc_id: str = Field(description="Bağlı olduğu doküman kimliği")
    title: str = Field(description="Doküman başlığı")
    section: str = Field(description="Bölüm başlığı")
    breadcrumbs: str = Field(description="Hiyerarşik yol bilgisi")
    text: str = Field(description="Parçanın temiz metin içeriği")
    rank: int = Field(description="Retrieval sıralama derecesi")
    score: float = Field(description="Retrieval hibrit benzerlik skoru")


class RAGContext(BaseModel):
    """Modele gönderilen yapılandırılmış ve etiketlenmiş kaynaklar kümesi."""
    model_config = ConfigDict(frozen=True)

    sources: List[SourceChunk] = Field(default_factory=list)
    formatted_text: str = Field(description="Modele prompt olarak verilecek formatlı context metni")
    total_tokens_estimate: int = Field(default=0)


class Claim(BaseModel):
    """Cevaptan ayrıştırılan tekil iddia veya önerme cümlesi."""
    model_config = ConfigDict(frozen=True)

    claim_id: int
    text: str = Field(description="Cümle veya iddia metni")
    cited_source_ids: List[str] = Field(default_factory=list, description="Cümlede geçen kaynak atıfları (örn: ['S1'])")
    is_cited: bool = Field(description="Cümlede en az bir atıf var mı?")


class ClaimVerification(BaseModel):
    """Tek bir iddianın kaynaklara sadakat ve doğruluk analizi."""
    model_config = ConfigDict(frozen=True)

    claim: Claim
    status: str = Field(description="SUPPORTED, HALLUCINATION, MISSING_CITATION, INVALID_SOURCE_ID")
    faithfulness_score: float = Field(description="[0.0, 1.0] Arasında kaynak metinsel örtüşme skoru")
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    explanation: str = Field(description="Doğrulama kararı gerekçesi")


class RAGResponse(BaseModel):
    """RAG motorunun ürettiği tam kaynaklı cevap ve doğrulama sonucu."""
    model_config = ConfigDict(frozen=True)

    query: str
    raw_answer: str = Field(description="Modelin ürettiği ham atıflı metin")
    cleaned_answer: str = Field(description="Atıf etiketleri temizlenmiş kullanıcı dostu metin")
    context: RAGContext
    claims: List[ClaimVerification] = Field(default_factory=list)
    is_refusal: bool = Field(default=False, description="Model bilgi yetersizliği nedeniyle cevap vermeyi reddetti mi?")
    overall_faithfulness: float = Field(description="Tüm iddiaların ortalama kaynak sadakati")
    citation_precision: float = Field(description="Doğru kaynak gösterilen atıf oranı")
    citation_recall: float = Field(description="Atıf yapılması gereken iddialara atıf yapılma oranı")
    hallucination_detected: bool = Field(default=False)
    latency_ms: float = Field(default=0.0)


class RAGEvalItem(BaseModel):
    """Değerlendirme veri setindeki bir sorgunun uçtan uca RAG analiz kaydı."""
    model_config = ConfigDict(frozen=True)

    query_id: str
    query: str
    category: str
    expected_behavior: str = Field(description="FAITHFUL_ANSWER veya REFUSAL")
    actual_behavior: str = Field(description="ANSWER_GENERATED veya REFUSAL")
    retrieval_hit: bool = Field(description="Hedef chunk Top-K context içinde yer aldı mı?")
    retrieval_target_rank: Optional[int] = None
    generation_faithful: bool = Field(description="Cevaptaki iddialar kaynakla örtüştü mü?")
    hallucination_detected: bool
    error_type: str = Field(description="SUCCESS, RETRIEVAL_FAILURE, GENERATION_HALLUCINATION, CORRECT_ABSTENTION, FAILED_ABSTENTION")
    rag_response: RAGResponse


class RAGEvaluationReport(BaseModel):
    """Tüm altın sorguların RAG başarım ve doğruluk konsolide raporu."""
    model_config = ConfigDict(frozen=True)

    generated_at: str
    total_queries: int
    success_count: int
    retrieval_failures: int
    generation_hallucinations: int
    correct_abstentions: int
    mean_faithfulness: float
    citation_precision: float
    citation_recall: float
    items: List[RAGEvalItem] = Field(default_factory=list)
