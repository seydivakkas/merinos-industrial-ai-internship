"""
Merinos Industrial AI Internship - Day 29 (Phase 5: Fine-Tuning & LLM Customization)
Pydantic v2 Data Models for SLM Evaluation, Nano-LLM Architecture, Hardware Profiling & Quantization.

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class ModelCandidateSpec(BaseModel):
    """Açık kaynaklı küçük dil modeli (SLM) mimari ve bellek spesifikasyonu."""
    model_id: str = Field(description="Model kimliği (örn: qwen2.5-0.5b)")
    model_name: str = Field(description="Tam model adı")
    developer: str = Field(description="Geliştirici kurum")
    params_billion: float = Field(description="Milyar cinsinden parametre sayısı")
    architecture: str = Field(description="Temel mimari tipi")
    d_model: int = Field(description="Gizli katman boyutu")
    n_heads: int = Field(description="Dikkat başlığı sayısı")
    n_kv_heads: int = Field(description="KV dikkat başlığı sayısı (GQA için)")
    n_layers: int = Field(description="Transformer katman sayısı")
    vocab_size: int = Field(description="Kelime dağarcığı büyüklüğü")
    max_context: int = Field(description="Maksimum bağlam penceresi")
    mmlu_score: float = Field(description="MMLU doğruluk skoru")
    fp32_ram_gb: float = Field(description="FP32 model ağırlık belleği (GB)")
    fp16_ram_gb: float = Field(description="FP16 model ağırlık belleği (GB)")
    int8_ram_gb: float = Field(description="INT8 kuantalanmış model ağırlık belleği (GB)")
    int4_ram_gb: float = Field(description="INT4 kuantalanmış model ağırlık belleği (GB)")
    recommended_for: str = Field(description="Merinos fabrikasındaki kullanım alanı")


class HardwareTarget(BaseModel):
    """Merinos fabrika yerel veya uç (edge) donanım profili."""
    name: str = Field(description="Donanım / GPU adı")
    vram_gb: float = Field(description="Kullanılabilir VRAM / Bellek (GB)")
    memory_bandwidth_gbs: float = Field(description="Bellek bant genişliği (GB/s)")
    fp16_tflops: float = Field(description="FP16 tepe hesaplama gücü (TFLOPS)")
    int8_tops: float = Field(description="INT8 tepe hesaplama gücü (TOPS)")
    tpd_watts: int = Field(description="Güç tüketimi (Watt)")


class QuantizationDetail(BaseModel):
    """Kuantalama hassasiyeti ve bellek tasarruf analizi."""
    precision_type: str = Field(description="Hassasiyet tipi (FP32, FP16, INT8, INT4)")
    bits_per_param: int = Field(description="Parametre başına bit sayısı")
    bytes_per_param: float = Field(description="Parametre başına bayt")
    model_size_gb: float = Field(description="Model ağırlık boyutu (GB)")
    kv_cache_per_1k_tokens_mb: float = Field(description="1000 token için KV önbellek boyutu (MB)")
    compression_ratio: float = Field(description="FP32'ye kıyasla sıkıştırma oranı")
    estimated_speedup: float = Field(description="Tahmini bellek-bağlantılı hızlanma faktörü")


class RooflinePoint(BaseModel):
    """Roofline modeli üzerinde hesaplanan operasyon noktası."""
    hardware_name: str
    arithmetic_intensity: float = Field(description="Aritmetik Yoğunluk (FLOP / Byte)")
    achievable_tflops: float = Field(description="Erişilebilir performans (TFLOPS)")
    operational_regime: str = Field(description="İşletim rejimi: 'memory_bound' veya 'compute_bound'")
    efficiency_pct: float = Field(description="Donanım tepe kapasitesi kullanım verimliliği (%)")


class NanoLLMConfig(BaseModel):
    """Sıfırdan geliştirilen Merinos Nano-LLM mimari hiperparametreleri."""
    model_name: str = Field(default="MerinosNanoLLM-32M")
    vocab_size: int = Field(default=1024, description="Kelime dağarcığı")
    d_model: int = Field(default=192, description="Gömme boyutu")
    n_heads: int = Field(default=6, description="Sorgu başlık sayısı")
    n_kv_heads: int = Field(default=2, description="KV başlık sayısı (Grouped Query Attention)")
    n_layers: int = Field(default=4, description="Transformer blok sayısı")
    intermediate_size: int = Field(default=512, description="SwiGLU ara boyut")
    max_seq_len: int = Field(default=256, description="Maksimum dizi uzunluğu")
    rope_theta: float = Field(default=10000.0, description="RoPE frekans tabanı")
    rms_norm_eps: float = Field(default=1e-6, description="RMSNorm epsilon değeri")
    dropout: float = Field(default=0.05, description="Dropout olasılığı")
    # Modern mimari eklentileri (MoE, DeepSeek Shared Expert, KV Cache, Logit Soft-Capping)
    use_moe: bool = Field(default=False, description="Sparse Mixture of Experts (MoE) aktif mi?")
    num_experts: int = Field(default=4, description="Toplam uzman (expert) sayısı")
    num_experts_per_tok: int = Field(default=2, description="Token başına yönlendirilen uzman sayısı (Top-K)")
    use_shared_expert: bool = Field(default=True, description="DeepSeek-V2/V3 tarzı daimi aktif paylaşılan uzman")
    enable_kv_cache: bool = Field(default=True, description="Hızlı otoregresif çıkarım için KV önbellekleme")
    attention_logit_soft_capping: Optional[float] = Field(default=None, description="Gemma-2 tarzı dikkat logit yumuşatma eşiği")
    aux_loss_coef: float = Field(default=0.01, description="MoE yük dengeleme yardımcı kayıp katsayısı")


class GenerationRequest(BaseModel):
    """Autoregressive metin tamamlama isteği."""
    model_config = ConfigDict(populate_by_name=True)

    prompt: str = Field(description="Girdi metni / arıza başlangıcı")
    max_tokens: int = Field(default=32, ge=1, le=256, description="Üretilecek azami token sayısı")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Rastlantısallık katsayısı")
    top_k: int = Field(default=40, ge=1, description="Top-K filtreleme eşiği")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Nucleus sampling eşiği")


class GenerationResponse(BaseModel):
    """Autoregressive metin tamamlama cevabı."""
    prompt: str
    generated_text: str
    full_text: str
    tokens_generated: int
    generation_time_ms: float
    tokens_per_second: float
    perplexity: float


class BackendComparisonItem(BaseModel):
    """PyTorch ve TensorFlow fonksiyonel eşdeğerlik öğesi."""
    category: str
    operation_name: str
    pytorch_syntax: str
    tensorflow_syntax: str
    description: str
    mathematical_concept: str


# ============================================================================
# ISO 14224 Güvenilirlik & Bakım Taksonomisi ve Karar Destek Veri Modelleri
# ============================================================================

class ISO14224TaxonomyNode(BaseModel):
    """ISO 14224 9 seviyeli endüstriyel varlık hiyerarşisi modeli."""
    model_config = ConfigDict(populate_by_name=True)

    plant_site: str = Field(default="MER-T01", description="Seviye 1-3: Tesis Kampüsü (Merinos Gaziantep 4. OSB)")
    area_line: str = Field(description="Seviye 4: Üretim Alanı / Salon (Örn: LN-W02 Dokuma Salonu 2)")
    equipment_unit: str = Field(description="Seviye 6: Fiziksel Ana Ekipman (Örn: VDW-RCE2-14)")
    sub_unit: str = Field(description="Seviye 7: Alt Sistem / Fonksiyonel Grup (Örn: ATK-01 Atkı Atma)")
    maintainable_item: str = Field(description="Seviye 8: Bakım Edilebilir Öğe (Örn: GRP-R01 Sağ Rapyer Kıskacı)")
    part: Optional[str] = Field(default=None, description="Seviye 9: En Alt Parça (Örn: SPR-092 Kıskaç Baskı Yayı)")


class ISO14224FailureRecord(BaseModel):
    """ISO 14224 standardına uygun arıza modu, mekanizması ve kök neden modeli."""
    model_config = ConfigDict(populate_by_name=True)

    iso_fault_code: str = Field(description="ISO 14224 standart arıza kodu (Örn: MEC-TRN-BRK, ELC-MOD-SHR)")
    failure_mode: str = Field(description="Arıza Modu: Dışarıdan gözlemlenen işlev kaybı")
    failure_mechanism: str = Field(description="Arıza Mekanizması: Fiziksel/kimyasal bozulma süreci")
    failure_cause: str = Field(description="Arıza Nedeni: Olayı tetikleyen kök etken")
    detection_method: str = Field(description="Tespit Yöntemi: Sinyal, sensör veya görsel tespit")
    corrective_action: str = Field(description="Düzeltici / Önleyici Bakım Eylemi")


class ReliabilityMetrics(BaseModel):
    """ISO 14224 Ek C güvenilirlik ve parça ömrü matematiksel modelleri."""
    model_config = ConfigDict(populate_by_name=True)

    cumulative_failures_n: int = Field(default=0, ge=0, description="Kümülatif arıza sayısı (n)")
    operating_time_hours_t: float = Field(default=1.0, gt=0.0, description="Kümülatif çalışma süresi saat (t)")
    operational_speed_xi: float = Field(default=180.0, gt=0.0, description="Operasyonel hız (rpm veya m/dk)")
    
    # Hesaplanmış metrikler
    failure_rate_lambda: float = Field(description="Laplace düzeltmeli arıza oranı (λ = (n + 0.7) / t)")
    mtbf_hours: float = Field(description="Arızalar arası ortalama süre (saat)")
    mctf_cycles: float = Field(description="Arızalar arası ortalama çevrim (vuruş/çevrim sayısı)")
    mttf_hours: float = Field(description="Arızaya kadar ortalama süre (saat) = MCTF / ξ")
    availability_ao_pct: float = Field(description="Teknik kullanılabilirlik yüzdesi (%)")

    @classmethod
    def calculate(cls, n: int, t: float, xi: float, mttr_hours: float = 0.5) -> "ReliabilityMetrics":
        """ISO 14224 Ek C matematiksel güvenilirlik formülleriyle hesaplama yapar."""
        fail_rate = (n + 0.7) / max(t, 1e-4)
        mtbf = 1.0 / fail_rate if fail_rate > 0 else t
        mctf = mtbf * (xi * 60.0)  # rpm -> saatlik vuruş
        mttf = mctf / (xi * 60.0)
        avail = (mtbf / (mtbf + mttr_hours)) * 100.0 if (mtbf + mttr_hours) > 0 else 100.0
        return cls(
            cumulative_failures_n=n,
            operating_time_hours_t=round(t, 2),
            operational_speed_xi=round(xi, 2),
            failure_rate_lambda=round(fail_rate, 6),
            mtbf_hours=round(mtbf, 2),
            mctf_cycles=round(mctf, 0),
            mttf_hours=round(mttf, 2),
            availability_ao_pct=round(avail, 2)
        )


class MaintenanceDecisionCard(BaseModel):
    """Teknisyene sunulan çok modlu RAG ajan karar destek kartı."""
    model_config = ConfigDict(populate_by_name=True)

    equipment_code: str
    iso_taxonomy: ISO14224TaxonomyNode
    failure_record: ISO14224FailureRecord
    reliability_analysis: ReliabilityMetrics
    loto_mandatory: bool = True
    loto_protocol_steps: List[str]
    maintenance_sop_steps: List[str]
    citations: List[Dict[str, Any]] = Field(description="OEM PDF ve şema sayfa alıntıları (Citation Grounding)")
    spare_parts: List[Dict[str, Any]] = Field(description="SAP PM / ERP ambar stok ve raf bilgileri")
    confidence_score: float = Field(ge=0.0, le=1.0)

