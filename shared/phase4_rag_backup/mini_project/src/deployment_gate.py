"""
Merinos Industrial AI Internship - Day 28 (Phase 4 Capstone)
Automated Ragas Deployment Quality Gate for Production CI/CD Pipelines

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional
from day28.mini_project.src.models import GateCheckResult, QueryRequest
from day28.mini_project.src.hybrid_retriever import HybridRetriever
from day28.mini_project.src.generator_llm import GroundedGenerator
from day27.mini_project.src.ragas_engine import MerinosRagasEngine
from day27.mini_project.src.models import EvalSample


class DeploymentGate:
    """Üretim Ortamına Geçiş Kalite ve Güvenlik Denetim Kapısı."""

    def __init__(
        self,
        retriever: HybridRetriever,
        generator: GroundedGenerator,
        thresholds: Optional[Dict[str, float]] = None
    ):
        self.retriever = retriever
        self.generator = generator
        self.thresholds = thresholds or {
            "min_faithfulness": 0.80,
            "min_context_precision": 0.80,
            "min_context_recall": 0.75,
            "min_answer_relevance": 0.75,
            "min_composite_ragas": 0.82
        }
        self.ragas_engine = MerinosRagasEngine()

    def run_gate_audit(self, test_queries: List[Dict[str, Any]]) -> GateCheckResult:
        """Tüm test sorgularını uçtan uca çalıştırır ve Ragas kapı kriterlerini denetler."""
        eval_samples: List[EvalSample] = []

        for q_item in test_queries:
            req = QueryRequest(
                query=q_item["query"],
                department_filter=q_item.get("department"),
                machine_filter=q_item.get("machine"),
                top_k=3,
                enable_reranking=True
            )
            candidates, lats = self.retriever.retrieve(req)
            gen_resp = self.generator.generate(req, candidates, lats)

            contexts = [c.text for c in candidates] if candidates else [""]

            eval_samples.append(
                EvalSample(
                    question_id=q_item.get("query_id", "Q_TEST"),
                    question=q_item["query"],
                    department=q_item.get("department", "genel"),
                    machine=q_item.get("machine", "genel"),
                    ground_truth=q_item.get("gold_fact", q_item.get("ground_truth", "")),
                    contexts=contexts,
                    answer=gen_resp.answer,
                    pipeline_id="integrated_capstone_rag"
                )
            )

        summary, evaluations = self.ragas_engine.evaluate_pipeline(
            samples=eval_samples,
            pipeline_id="integrated_capstone_rag",
            pipeline_name="Merinos Integrated Phase 4 RAG Pipeline"
        )

        reasons = []
        passed = True

        if summary.avg_faithfulness < self.thresholds["min_faithfulness"]:
            passed = False
            reasons.append(f"Sadakat (Faithfulness) %{summary.avg_faithfulness*100:.1f} < eşik %{self.thresholds['min_faithfulness']*100:.1f}")

        if summary.avg_context_precision < self.thresholds["min_context_precision"]:
            passed = False
            reasons.append(f"Bağlamsal Kesinlik %{summary.avg_context_precision*100:.1f} < eşik %{self.thresholds['min_context_precision']*100:.1f}")

        if summary.avg_context_recall < self.thresholds["min_context_recall"]:
            passed = False
            reasons.append(f"Bağlamsal Kapsama %{summary.avg_context_recall*100:.1f} < eşik %{self.thresholds['min_context_recall']*100:.1f}")

        if summary.avg_answer_relevance < self.thresholds["min_answer_relevance"]:
            passed = False
            reasons.append(f"Cevap Uygunluğu %{summary.avg_answer_relevance*100:.1f} < eşik %{self.thresholds['min_answer_relevance']*100:.1f}")

        if summary.avg_ragas_composite < self.thresholds["min_composite_ragas"]:
            passed = False
            reasons.append(f"Harmonik Ragas Skoru %{summary.avg_ragas_composite*100:.1f} < eşik %{self.thresholds['min_composite_ragas']*100:.1f}")

        if passed:
            reasons.append("Tüm kalite, sadakat ve bağlamsal doğruluk kriterleri sağlandı. CANLI DAĞITIM ONAYLANDI.")

        return GateCheckResult(
            passed=passed,
            faithfulness=summary.avg_faithfulness,
            context_precision=summary.avg_context_precision,
            context_recall=summary.avg_context_recall,
            answer_relevance=summary.avg_answer_relevance,
            ragas_composite=summary.avg_ragas_composite,
            thresholds=self.thresholds,
            reasons=reasons,
            audit_details={
                "num_test_queries": len(test_queries),
                "per_department": summary.per_department_scores
            }
        )
