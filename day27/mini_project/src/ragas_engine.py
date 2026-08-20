"""
Merinos Industrial AI Internship - Day 27
Unified Ragas Evaluation Engine for Industrial RAG Pipelines

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from day27.mini_project.src.models import (
    EvalSample,
    SampleEvaluation,
    PipelineSummary,
    RagasBenchmarkReport
)
from day27.mini_project.src.claim_extractor import ClaimExtractor
from day27.mini_project.src.context_metrics import ContextPrecisionEvaluator, ContextRecallEvaluator
from day27.mini_project.src.generation_metrics import FaithfulnessEvaluator, AnswerRelevanceEvaluator


class MerinosRagasEngine:
    """Merinos Endüstriyel RAG Değerlendirme ve Ragas Metrik Orkestratörü."""

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, float]] = None
    ):
        self.weights = weights or {
            "faithfulness": 0.30,
            "context_precision": 0.25,
            "context_recall": 0.25,
            "answer_relevance": 0.20
        }
        self.thresholds = thresholds or {
            "faithfulness_min": 0.75,
            "context_precision_min": 0.70,
            "context_recall_min": 0.70,
            "answer_relevance_min": 0.70,
            "ragas_composite_min": 0.72
        }

        self.claim_extractor = ClaimExtractor()
        self.context_precision_evaluator = ContextPrecisionEvaluator()
        self.context_recall_evaluator = ContextRecallEvaluator(self.claim_extractor)
        self.faithfulness_evaluator = FaithfulnessEvaluator(self.claim_extractor)
        self.answer_relevance_evaluator = AnswerRelevanceEvaluator(self.claim_extractor)

    def compute_composite_score(
        self,
        faithfulness: float,
        context_precision: float,
        context_recall: float,
        answer_relevance: float,
        method: str = "harmonic"
    ) -> float:
        """4 metriğin bileşik Ragas skorunu hesaplar (Harmonik Ortalama veya Ağırlıklı Ortalama)."""
        eps = 1e-6
        if method == "harmonic":
            # Harmonik ortalama: Herhangi bir metriğin sıfıra yakın olması durumunda skoru cezalandırır
            inv_sum = (
                (1.0 / (faithfulness + eps)) +
                (1.0 / (context_precision + eps)) +
                (1.0 / (context_recall + eps)) +
                (1.0 / (answer_relevance + eps))
            )
            return float(max(0.0, min(1.0, 4.0 / inv_sum)))
        else:
            w = self.weights
            score = (
                w.get("faithfulness", 0.3) * faithfulness +
                w.get("context_precision", 0.25) * context_precision +
                w.get("context_recall", 0.25) * context_recall +
                w.get("answer_relevance", 0.2) * answer_relevance
            )
            return float(max(0.0, min(1.0, score)))

    def evaluate_sample(self, sample: EvalSample) -> SampleEvaluation:
        """Tek bir RAG örneğini 4 Ragas metriğinde değerlendirir."""
        # 1. Context Precision
        cp_metric = self.context_precision_evaluator.evaluate(
            sample.contexts, sample.ground_truth, sample.question
        )

        # 2. Context Recall
        cr_metric = self.context_recall_evaluator.evaluate(
            sample.contexts, sample.ground_truth
        )

        # 3. Faithfulness (Halüsinasyon)
        f_metric, claims = self.faithfulness_evaluator.evaluate(
            sample.contexts, sample.answer
        )

        # 4. Answer Relevance
        ar_metric = self.answer_relevance_evaluator.evaluate(
            sample.question, sample.answer
        )

        # 5. Bileşik Ragas Skoru
        composite = self.compute_composite_score(
            faithfulness=f_metric.score,
            context_precision=cp_metric.score,
            context_recall=cr_metric.score,
            answer_relevance=ar_metric.score,
            method="harmonic"
        )

        return SampleEvaluation(
            question_id=sample.question_id,
            pipeline_id=sample.pipeline_id,
            department=sample.department,
            machine=sample.machine,
            faithfulness=round(f_metric.score, 4),
            context_precision=round(cp_metric.score, 4),
            context_recall=round(cr_metric.score, 4),
            answer_relevance=round(ar_metric.score, 4),
            ragas_composite_score=round(composite, 4),
            claims=claims,
            details={
                "context_precision_details": cp_metric.details,
                "context_recall_details": cr_metric.details,
                "faithfulness_details": f_metric.details,
                "answer_relevance_details": ar_metric.details
            }
        )

    def evaluate_pipeline(
        self,
        samples: List[EvalSample],
        pipeline_id: str,
        pipeline_name: str
    ) -> (PipelineSummary, List[SampleEvaluation]):
        """Bir RAG pipeline'ına ait tüm örnekleri değerlendirip özet üretir."""
        evaluations: List[SampleEvaluation] = []
        dept_scores: Dict[str, List[float]] = {}

        for s in samples:
            s.pipeline_id = pipeline_id
            ev = self.evaluate_sample(s)
            evaluations.append(ev)

            dept = s.department
            if dept not in dept_scores:
                dept_scores[dept] = []
            dept_scores[dept].append(ev.ragas_composite_score)

        n = len(evaluations)
        if n == 0:
            summary = PipelineSummary(
                pipeline_id=pipeline_id,
                pipeline_name=pipeline_name,
                num_samples=0,
                avg_faithfulness=0.0,
                avg_context_precision=0.0,
                avg_context_recall=0.0,
                avg_answer_relevance=0.0,
                avg_ragas_composite=0.0
            )
            return summary, []

        avg_f = sum(e.faithfulness for e in evaluations) / n
        avg_cp = sum(e.context_precision for e in evaluations) / n
        avg_cr = sum(e.context_recall for e in evaluations) / n
        avg_ar = sum(e.answer_relevance for e in evaluations) / n
        avg_comp = sum(e.ragas_composite_score for e in evaluations) / n

        per_dept_avg = {
            dept: {"avg_composite": round(sum(scores) / len(scores), 4), "count": len(scores)}
            for dept, scores in dept_scores.items()
        }

        summary = PipelineSummary(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            num_samples=n,
            avg_faithfulness=round(avg_f, 4),
            avg_context_precision=round(avg_cp, 4),
            avg_context_recall=round(avg_cr, 4),
            avg_answer_relevance=round(avg_ar, 4),
            avg_ragas_composite=round(avg_comp, 4),
            per_department_scores=per_dept_avg
        )
        return summary, evaluations

    def run_full_benchmark(self, raw_dataset: List[Dict[str, Any]]) -> RagasBenchmarkReport:
        """3 farklı RAG mimarisini 20 Merinos senaryosu üzerinde kıyaslar."""
        pipeline_defs = [
            ("pipeline_a", "Vanilla BM25 RAG", "contexts_pipeline_a", "answer_pipeline_a"),
            ("pipeline_b", "Dense Vector RAG", "contexts_pipeline_b", "answer_pipeline_b"),
            ("pipeline_c", "Hybrid RRF + Reranked RAG", "contexts_pipeline_c", "answer_pipeline_c")
        ]

        pipeline_summaries: List[PipelineSummary] = []
        all_sample_evals: List[SampleEvaluation] = []

        for p_id, p_name, ctx_key, ans_key in pipeline_defs:
            samples = []
            for item in raw_dataset:
                samples.append(
                    EvalSample(
                        question_id=item["question_id"],
                        question=item["question"],
                        department=item["department"],
                        machine=item["machine"],
                        ground_truth=item["ground_truth"],
                        contexts=item[ctx_key],
                        answer=item[ans_key],
                        pipeline_id=p_id
                    )
                )

            p_summary, p_evals = self.evaluate_pipeline(samples, p_id, p_name)
            pipeline_summaries.append(p_summary)
            all_sample_evals.extend(p_evals)

        # En başarılı pipeline'ı seç
        best_pipe = max(pipeline_summaries, key=lambda x: x.avg_ragas_composite)

        # Eşik kontrolleri
        threshold_comp = {
            "faithfulness_met": best_pipe.avg_faithfulness >= self.thresholds.get("faithfulness_min", 0.75),
            "context_precision_met": best_pipe.avg_context_precision >= self.thresholds.get("context_precision_min", 0.70),
            "context_recall_met": best_pipe.avg_context_recall >= self.thresholds.get("context_recall_min", 0.70),
            "answer_relevance_met": best_pipe.avg_answer_relevance >= self.thresholds.get("answer_relevance_min", 0.70),
            "composite_score_met": best_pipe.avg_ragas_composite >= self.thresholds.get("ragas_composite_min", 0.72)
        }

        report = RagasBenchmarkReport(
            benchmark_name="Merinos Industrial RAG Retrieval & Generation Assessment",
            timestamp=datetime.now().isoformat(),
            sample_count=len(raw_dataset),
            pipelines=pipeline_summaries,
            sample_evaluations=all_sample_evals,
            best_pipeline_id=best_pipe.pipeline_id,
            best_ragas_score=best_pipe.avg_ragas_composite,
            threshold_compliance=threshold_comp
        )
        return report
