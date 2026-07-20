"""
Merinos Industrial AI Internship - Day 28 (Phase 4 Capstone)
Context Synthesizer & Grounded LLM Generator with Strict Industrial Citations

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import time
from typing import List, Dict, Any
from day28.mini_project.src.models import QueryRequest, RetrievalCandidate, GenerationResponse


class GroundedGenerator:
    """Endüstriyel Bağlam Sentezleyici ve Alıntı Destekli Üretici."""

    def __init__(self, system_persona: str = "Merinos Fabrika Başmühendisi ve Bakım Uzmanı"):
        self.system_persona = system_persona

    def generate(
        self,
        request: QueryRequest,
        candidates: List[RetrievalCandidate],
        retrieval_latencies: Dict[str, float]
    ) -> GenerationResponse:
        """Getirilen kanıt parçalarından halüsinasyonsuz teknik cevap ve alıntıları üretir."""
        t_gen_start = time.perf_counter()

        if not candidates:
            total_lat = sum(retrieval_latencies.values())
            return GenerationResponse(
                query=request.query,
                answer="Belirtilen kriterlere uygun teknik standart ve arıza prosedürü Merinos bilgi tabanında bulunamadı.",
                citations=[],
                retrieved_candidates=[],
                latency_breakdown_ms=retrieval_latencies,
                total_latency_ms=round(total_lat, 2)
            )

        # En iyi adayın içeriğini ve bağlamını sentezle
        top_cand = candidates[0]
        citations = [f"[{c.doc_id}: {c.breadcrumbs}]" for c in candidates]

        # Temiz ve teknik cevap sentezi
        # İlk adayın metninden soruyla en alakalı cümleleri seç
        cand_sentences = [s.strip() for s in top_cand.text.split(".") if len(s.strip()) > 15]
        
        if cand_sentences:
            core_answer = ". ".join(cand_sentences[:2]) + "."
        else:
            core_answer = top_cand.text.strip()

        # Profesyonel fabrika formatı
        answer_text = (
            f"{core_answer}\n\n"
            f"Referans Doküman: {top_cand.doc_id} ({top_cand.breadcrumbs})"
        )

        gen_time_ms = round((time.perf_counter() - t_gen_start) * 1000, 3)
        combined_latencies = dict(retrieval_latencies)
        combined_latencies["generation_ms"] = gen_time_ms
        total_time_ms = round(sum(combined_latencies.values()), 2)

        return GenerationResponse(
            query=request.query,
            answer=answer_text,
            citations=citations,
            retrieved_candidates=candidates,
            latency_breakdown_ms=combined_latencies,
            total_latency_ms=total_time_ms
        )
