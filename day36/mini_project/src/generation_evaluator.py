# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 36
Generation Evaluator: 15 Altın Senaryoda Groundedness, Alıntı ve Halüsinasyon Benchmark Motoru
"""

import time
import json
import datetime
from pathlib import Path
from typing import List, Dict, Optional

from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day36.mini_project.src.models import (
    StructuredAnswer,
    GenerationBenchmarkItem,
    GenerationBenchmarkReport
)
from day36.mini_project.src.structured_generator import StructuredGenerator
from day36.mini_project.src.groundedness_checker import GroundednessChecker


class GenerationEvaluator:
    """
    Getirilen parçalar ve operatör soruları üzerinden yapılandırılmış yanıt üretimini,
    bağlama sadakati (Faithfulness) ve alıntı kesinliğini değerlendiren kıyaslama yöneticisi.
    """

    def __init__(
        self,
        knowledge_manager: KnowledgeManager,
        hybrid_retriever: HybridRetriever,
        generator: Optional[StructuredGenerator] = None,
        checker: Optional[GroundednessChecker] = None,
        top_k: int = 3
    ):
        self.km = knowledge_manager
        self.hybrid = hybrid_retriever
        self.generator = generator or StructuredGenerator()
        self.checker = checker or GroundednessChecker(threshold=0.60)
        self.top_k = top_k
        self.chunk_lookup = {c.chunk_id: c for c in self.km.chunks}

    def evaluate_scenario(self, scenario: Dict) -> GenerationBenchmarkItem:
        """Tek bir benchmark senaryosunu uçtan uca test eder."""
        sid = scenario["id"]
        query = scenario["query"]
        category = scenario.get("category", "GENERAL")
        is_adversarial = scenario.get("is_adversarial", False)

        t0 = time.perf_counter()

        # 1. Bilgi Getirme (Top-K=3)
        retrieval_res = self.hybrid.search(query, method="linear", top_k=self.top_k, alpha=0.5)
        retrieved_chunks = [self.chunk_lookup[it.chunk_id] for it in retrieval_res.items if it.chunk_id in self.chunk_lookup]

        # 2. Yanıt Üretimi
        answer = self.generator.generate(query, retrieved_chunks)

        # 3. Groundedness ve Alıntı Denetimi
        metric, _ = self.checker.evaluate_answer(answer, retrieved_chunks)

        dt = (time.perf_counter() - t0) * 1000.0

        fallback_correct = (answer.fallback_triggered == is_adversarial)

        return GenerationBenchmarkItem(
            scenario_id=sid,
            query=query,
            category=category,
            is_adversarial=is_adversarial,
            fallback_triggered=answer.fallback_triggered,
            fallback_correct=fallback_correct,
            faithfulness_rate=metric.faithfulness_rate,
            citation_precision=metric.citation_precision,
            citation_recall=metric.citation_recall,
            has_safety_alert=bool(answer.safety_alert),
            latency_ms=round(dt, 2),
            answer=answer
        )

    def run_benchmark(self, dataset_path: str) -> GenerationBenchmarkReport:
        """Tüm senaryoları çalıştırıp toplu kalite ve güvenlik raporunu üretir."""
        with open(dataset_path, "r", encoding="utf-8") as f:
            scenarios = json.load(f)

        items: List[GenerationBenchmarkItem] = []
        valid_items: List[GenerationBenchmarkItem] = []
        adv_items: List[GenerationBenchmarkItem] = []

        for sc in scenarios:
            item = self.evaluate_scenario(sc)
            items.append(item)
            if item.is_adversarial:
                adv_items.append(item)
            else:
                valid_items.append(item)

        # Metrik Ortalamaları
        v_count = len(valid_items)
        mean_faith = sum(it.faithfulness_rate for it in valid_items) / v_count if v_count else 1.0
        mean_prec = sum(it.citation_precision for it in valid_items) / v_count if v_count else 1.0
        mean_rec = sum(it.citation_recall for it in valid_items) / v_count if v_count else 1.0

        # Tuzak/Alan dışı fallback başarısı
        adv_count = len(adv_items)
        correct_fallbacks = sum(1 for it in adv_items if it.fallback_correct)
        fallback_acc = (correct_fallbacks / adv_count) if adv_count else 1.0

        avg_lat = sum(it.latency_ms for it in items) / len(items) if items else 0.0

        return GenerationBenchmarkReport(
            timestamp=datetime.datetime.now().isoformat(),
            total_scenarios=len(items),
            valid_domain_scenarios=v_count,
            adversarial_scenarios=adv_count,
            mean_faithfulness_rate=round(mean_faith, 4),
            mean_citation_precision=round(mean_prec, 4),
            mean_citation_recall=round(mean_rec, 4),
            adversarial_fallback_accuracy=round(fallback_acc, 4),
            avg_latency_ms=round(avg_lat, 2),
            items=items
        )
