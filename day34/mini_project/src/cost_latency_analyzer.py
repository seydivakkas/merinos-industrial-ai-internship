# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 34
Cost & Latency Analyzer: Context Sıkıştırma ve LLM Maliyet/Gecikme Modeli
"""

from typing import List
from day34.mini_project.src.models import (
    CandidateChunk,
    RerankedChunk,
    CompressionMetric,
    CostLatencyProfile
)


def estimate_token_count(text: str) -> int:
    """Metnin yaklaşık token adedini hesaplar (1 kelime ≈ 1.3 token)."""
    words = len(text.split())
    return max(int(words * 1.3), 1)


class CostLatencyAnalyzer:
    """
    Context Window sıkıştırmasının getirdiği token tasarrufunu,
    LLM API maliyet azalmasını ve uçtan uca gecikme kazancını modelleyen analizör.
    """

    def __init__(
        self,
        input_cost_per_1k_tokens: float = 0.0015,
        output_cost_per_1k_tokens: float = 0.0020,
        llm_base_latency_ms: float = 60.0,
        llm_ms_per_100_input_tokens: float = 8.0
    ):
        self.input_cost_per_1k_tokens = input_cost_per_1k_tokens
        self.output_cost_per_1k_tokens = output_cost_per_1k_tokens
        self.llm_base_latency_ms = llm_base_latency_ms
        self.llm_ms_per_100_input_tokens = llm_ms_per_100_input_tokens

    def analyze_compression(
        self,
        raw_candidates: List[CandidateChunk],
        reranked_chunks: List[RerankedChunk]
    ) -> CompressionMetric:
        """K1 aday parça ile K2 filtrelenmiş parça arasındaki sıkıştırma metriklerini hesaplar."""
        raw_tokens = sum(estimate_token_count(c.text) for c in raw_candidates)
        compressed_tokens = sum(estimate_token_count(r.text) for r in reranked_chunks)

        if raw_tokens == 0:
            return CompressionMetric(
                raw_tokens=0,
                compressed_tokens=0,
                tokens_saved=0,
                compression_ratio=0.0
            )

        tokens_saved = max(raw_tokens - compressed_tokens, 0)
        compression_ratio = round(tokens_saved / raw_tokens, 4)

        return CompressionMetric(
            raw_tokens=raw_tokens,
            compressed_tokens=compressed_tokens,
            tokens_saved=tokens_saved,
            compression_ratio=compression_ratio
        )

    def analyze_cost_and_latency(
        self,
        compression: CompressionMetric,
        reranker_overhead_ms: float
    ) -> CostLatencyProfile:
        """Token sıkıştırmasının finansal ve süre etkilerini hesaplar."""
        raw_tokens = compression.raw_tokens
        comp_tokens = compression.compressed_tokens

        # Maliyet Hesabı (USD)
        raw_input_cost = (raw_tokens / 1000.0) * self.input_cost_per_1k_tokens
        reranked_input_cost = (comp_tokens / 1000.0) * self.input_cost_per_1k_tokens
        cost_saving_usd = max(raw_input_cost - reranked_input_cost, 0.0)
        cost_saving_percent = round((cost_saving_usd / raw_input_cost * 100.0) if raw_input_cost > 0 else 0.0, 2)

        # Gecikme Hesabı (ms)
        # LLM TTFT (Time-To-First-Token) context uzunluğuyla doğru orantılıdır
        raw_llm_latency_ms = self.llm_base_latency_ms + (raw_tokens / 100.0) * self.llm_ms_per_100_input_tokens
        reranked_llm_latency_ms = self.llm_base_latency_ms + (comp_tokens / 100.0) * self.llm_ms_per_100_input_tokens

        net_latency_ms = reranker_overhead_ms + reranked_llm_latency_ms
        latency_delta_ms = raw_llm_latency_ms - net_latency_ms

        return CostLatencyProfile(
            raw_input_cost_usd=round(raw_input_cost, 6),
            reranked_input_cost_usd=round(reranked_input_cost, 6),
            cost_saving_usd=round(cost_saving_usd, 6),
            cost_saving_percent=cost_saving_percent,
            raw_llm_latency_ms=round(raw_llm_latency_ms, 2),
            reranked_llm_latency_ms=round(reranked_llm_latency_ms, 2),
            reranker_overhead_ms=round(reranker_overhead_ms, 2),
            net_latency_ms=round(net_latency_ms, 2),
            latency_delta_ms=round(latency_delta_ms, 2)
        )
