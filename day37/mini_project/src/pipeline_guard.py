# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 37
Pipeline Guard: Güvenlik Korkulukları ile Korunan Uçtan Uca RAG Orkestratörü
"""

import time
from typing import List, Dict, Optional, Any
from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day36.mini_project.src.structured_generator import StructuredGenerator
from day37.mini_project.src.models import (
    RagasMetrics,
    GuardrailDecision,
    EvaluationScenarioResult
)
from day37.mini_project.src.ragas_evaluator import RagasEvaluator
from day37.mini_project.src.safety_guardrails import SafetyGuardrails, GuardrailResult


class PipelineGuard:
    """
    Retrieval, Generation, Guardrails ve Ragas Evaluator adımlarını
    uçtan uca yöneten ve tehlikeli durumları anında engelleyen orkestratör.
    """

    def __init__(
        self,
        knowledge_manager: KnowledgeManager,
        hybrid_retriever: HybridRetriever,
        generator: Optional[StructuredGenerator] = None,
        evaluator: Optional[RagasEvaluator] = None,
        guardrails: Optional[SafetyGuardrails] = None,
        top_k: int = 3
    ):
        self.km = knowledge_manager
        self.hybrid = hybrid_retriever
        self.generator = generator or StructuredGenerator()
        self.evaluator = evaluator or RagasEvaluator()
        self.guardrails = guardrails or SafetyGuardrails()
        self.top_k = top_k
        self.chunk_lookup = {c.chunk_id: c for c in self.km.chunks}

    def process_query(
        self,
        scenario_id: str,
        query: str,
        category: str = "GENERAL",
        target_chunk_id: Optional[str] = None,
        ground_truth_claims: Optional[List[str]] = None,
        ground_truth_text: Optional[str] = None
    ) -> EvaluationScenarioResult:
        """
        Girdi kontrolü -> Bilgi getirme -> Yanıt üretimi -> Ragas metrikleri -> Çıktı kontrolü
        akışını işletir.
        """
        t0 = time.perf_counter()
        claims = ground_truth_claims or []

        # -------------------------------------------------------------
        # 1. GİRDİ GÜVENLİK FİLTRESİ (Input Guardrail)
        # -------------------------------------------------------------
        dec_in_raw = self.guardrails.check_input_safety(query)
        if isinstance(dec_in_raw, GuardrailResult):
            dec_in = dec_in_raw.to_decision()
        elif isinstance(dec_in_raw, GuardrailDecision):
            dec_in = dec_in_raw
        else:
            dec_in = GuardrailDecision(
                action="ALLOW" if dec_in_raw[0] else "BLOCK",
                reason=dec_in_raw[1],
                violation_category=dec_in_raw[2].get("type") if len(dec_in_raw) > 2 else None,
                sanitized_content="Bu talep güvenlik politikaları gereği işlenememektedir."
            )

        if dec_in.action == "BLOCK":
            dt = (time.perf_counter() - t0) * 1000.0
            metrics = RagasMetrics(
                context_precision=1.0,
                context_recall=1.0,
                faithfulness=1.0,
                answer_relevance=1.0,
                rag_triad_score=1.0
            )
            dec_out = GuardrailDecision(action="ALLOW", reason="Girdi aşamasında engellendi.")
            return EvaluationScenarioResult(
                scenario_id=scenario_id,
                query=query,
                category=category,
                input_guardrail=dec_in,
                output_guardrail=dec_out,
                metrics=metrics,
                final_answer=dec_in.sanitized_content or "Bu talep güvenlik politikaları gereği işlenememektedir.",
                is_blocked=True,
                latency_ms=round(dt, 2)
            )

        # -------------------------------------------------------------
        # 2. BİLGİ GETİRME (Retrieval: Top-K)
        # -------------------------------------------------------------
        ret_res = self.hybrid.search(query, method="linear", top_k=self.top_k, alpha=0.5)
        retrieved_chunks = [self.chunk_lookup[it.chunk_id] for it in ret_res.items if it.chunk_id in self.chunk_lookup]

        # -------------------------------------------------------------
        # 3. YANIT ÜRETİMİ (Generation)
        # -------------------------------------------------------------
        structured_ans = self.generator.generate(query, retrieved_chunks)
        raw_answer_text = structured_ans.direct_answer

        # -------------------------------------------------------------
        # 4. RAGAS METRİK DEĞERLENDİRMESİ
        # -------------------------------------------------------------
        metrics = self.evaluator.evaluate(
            query=query,
            retrieved_chunks=retrieved_chunks,
            answer_text=raw_answer_text,
            target_chunk_id=target_chunk_id,
            ground_truth_claims=claims,
            ground_truth_text=ground_truth_text
        )

        # -------------------------------------------------------------
        # 5. ÇIKTI GÜVENLİK FİLTRESİ (Output Guardrail)
        # -------------------------------------------------------------
        dec_out_raw = self.guardrails.check_output_safety(
            answer_text=raw_answer_text,
            retrieved_chunks=retrieved_chunks,
            faithfulness=metrics.faithfulness
        )
        if isinstance(dec_out_raw, GuardrailResult):
            dec_out = dec_out_raw.to_decision()
        elif isinstance(dec_out_raw, GuardrailDecision):
            dec_out = dec_out_raw
        else:
            dec_out = GuardrailDecision(
                action="ALLOW" if dec_out_raw[0] else "BLOCK",
                reason=dec_out_raw[1],
                violation_category=dec_out_raw[2].get("type") if len(dec_out_raw) > 2 else None,
                sanitized_content="Bu talep güvenlik politikaları gereği işlenememektedir."
            )

        final_ans = raw_answer_text
        is_blocked = False
        if dec_out.action == "BLOCK":
            final_ans = dec_out.sanitized_content or "GÜVENLİK FİLTRESİ: Yanıt engellendi."
            is_blocked = True

        dt = (time.perf_counter() - t0) * 1000.0

        return EvaluationScenarioResult(
            scenario_id=scenario_id,
            query=query,
            category=category,
            input_guardrail=dec_in,
            output_guardrail=dec_out,
            metrics=metrics,
            final_answer=final_ans,
            is_blocked=is_blocked,
            latency_ms=round(dt, 2)
        )
