# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 36
Birim ve Entegrasyon Testleri: Generation, Prompt Engineering, Citations & Groundedness
"""

import json
from pathlib import Path
import pytest

from day31.mini_project.src.models import ChunkRecord
from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.hybrid_retriever import HybridRetriever
from day36.mini_project.src.models import (
    CitationItem,
    StructuredAnswer,
    ClaimVerificationResult,
    GroundednessMetric
)
from day36.mini_project.src.prompt_builder import PromptBuilder
from day36.mini_project.src.structured_generator import StructuredGenerator
from day36.mini_project.src.groundedness_checker import GroundednessChecker
from day36.mini_project.src.generation_evaluator import GenerationEvaluator


# =====================================================================
# 1. PromptBuilder Testi: XML Ayracı ve Şablon Yapısı
# =====================================================================

def test_prompt_builder_structure_and_delimiters():
    pb = PromptBuilder()
    text = "E-401 motor sıcaklığı 85 dereceyi geçince tezgâh stop eder."
    mock_chunk = ChunkRecord(
        chunk_id="TEST_c001",
        doc_id="DOC_TEST",
        title="Test Dokümanı",
        source="DOC_TEST.md",
        section="Bakım",
        text=text,
        char_count=len(text),
        token_estimate=len(text) // 4
    )

    prompt = pb.build_prompt("Motor sıcaklığı ne olmalı?", [mock_chunk])
    assert "<retrieved_context>" in prompt
    assert "</retrieved_context>" in prompt
    assert '<doc id="TEST_c001"' in prompt
    assert "<operator_query>" in prompt
    assert "</operator_query>" in prompt
    assert "Merinos Halı Sanayi A.Ş." in prompt


# =====================================================================
# 2. StructuredAnswer Pydantic Doğrulama Testi
# =====================================================================

def test_structured_answer_pydantic_validation():
    cit = CitationItem(
        source_id="DOC_MERINOS_WEAVING_SOP",
        chunk_id="DOC_MERINOS_WEAVING_SOP_c004",
        quote="E-401 arıza kodu motorun aşırı ısındığını gösterir.",
        verified=True
    )
    ans = StructuredAnswer(
        query="Motor arıza kodu nedir?",
        direct_answer="E-401 motor aşırı ısınma kodudur.",
        action_steps=["Tezgâhı durdur.", "Filtreyi temizle."],
        technical_parameters={"arıza_kodu": "E-401", "kritik_sıcaklık": "85°C"},
        citations=[cit],
        safety_alert="DİKKAT: Motor aşırı ısınmıştır!",
        confidence_score=0.98,
        fallback_triggered=False
    )
    assert ans.confidence_score == 0.98
    assert len(ans.citations) == 1
    assert ans.citations[0].verified is True

    # JSON Serileştirme & Deserileştirme
    json_str = ans.model_dump_json()
    reloaded = StructuredAnswer.model_validate_json(json_str)
    assert reloaded.direct_answer == ans.direct_answer


# =====================================================================
# 3. Groundedness Checker: Desteklenen İddia Doğrulaması
# =====================================================================

def test_groundedness_checker_faithful_claim():
    checker = GroundednessChecker(threshold=0.60)
    text = "E-401 arıza kodu ana tahrik motoru aşırı ısınması durumunda devreye girer. Sıcaklık 85 dereceyi aşınca tezgâh durdurulur."
    mock_chunk = ChunkRecord(
        chunk_id="DOC_MERINOS_WEAVING_SOP_c004",
        doc_id="DOC_MERINOS_WEAVING_SOP",
        title="Dokuma SOP",
        source="DOC_MERINOS_WEAVING_SOP.md",
        section="Arızalar",
        text=text,
        char_count=len(text),
        token_estimate=len(text) // 4
    )

    faithful_claim = "E-401 arıza kodu motor sıcaklığı 85 dereceyi aşınca tezgâhı durdurur."
    res = checker.verify_claim(faithful_claim, [mock_chunk], cited_chunk_id=mock_chunk.chunk_id)
    assert res.is_supported is True
    assert res.verdict == "FAITHFUL"
    assert res.similarity_score >= 0.60


# =====================================================================
# 4. Groundedness Checker: Desteksiz / Halüsinasyon İddiası Tespiti
# =====================================================================

def test_groundedness_checker_unsupported_hallucination():
    checker = GroundednessChecker(threshold=0.60)
    text = "E-401 arıza kodu ana tahrik motoru aşırı ısınması durumunda devreye girer."
    mock_chunk = ChunkRecord(
        chunk_id="DOC_MERINOS_WEAVING_SOP_c004",
        doc_id="DOC_MERINOS_WEAVING_SOP",
        title="Dokuma SOP",
        source="DOC_MERINOS_WEAVING_SOP.md",
        section="Arızalar",
        text=text,
        char_count=len(text),
        token_estimate=len(text) // 4
    )

    # Dokümanda lazer sensörü veya E-999 hiç yok
    hallucinated_claim = "E-999 kodu tezgâhtaki kızılötesi lazer sensörünün kalibrasyon kaybını gösterir."
    res = checker.verify_claim(hallucinated_claim, [mock_chunk])
    assert res.is_supported is False
    assert res.verdict == "UNSUPPORTED"


# =====================================================================
# 5. Adversarial / Alan Dışı Güvenli Ret (Fallback) Testi
# =====================================================================

def test_adversarial_out_of_domain_fallback():
    gen = StructuredGenerator()
    text = "Dokuma tezgâhı levent ayarları ve armür hazırlığı."
    mock_chunk = ChunkRecord(
        chunk_id="DOC_MERINOS_WEAVING_SOP_c001",
        doc_id="DOC_MERINOS_WEAVING_SOP",
        title="Dokuma SOP",
        source="DOC_MERINOS_WEAVING_SOP.md",
        section="Genel",
        text=text,
        char_count=len(text),
        token_estimate=len(text) // 4
    )

    out_of_domain_query = "Fabrikadaki robot süpürgelerin şarj voltajı kaç volttur?"
    ans = gen.generate(out_of_domain_query, [mock_chunk])

    assert ans.fallback_triggered is True
    assert "bilgi bulunmamaktadır" in ans.direct_answer.lower()
    assert len(ans.citations) == 0


# =====================================================================
# 6. Uçtan Uca Generation Evaluator Benchmark Entegrasyon Testi
# =====================================================================

@pytest.fixture(scope="module")
def evaluator_instance():
    docs_dir = "day31/mini_project/fixtures/documents"
    km = KnowledgeManager(documents_dir=docs_dir)
    km.sync()

    hybrid = HybridRetriever(
        bm25=km.bm25,
        dense=km.dense,
        chunks=km.chunks,
        default_k_rrf=60,
        default_alpha=0.5
    )

    return GenerationEvaluator(
        knowledge_manager=km,
        hybrid_retriever=hybrid,
        generator=StructuredGenerator(),
        checker=GroundednessChecker(threshold=0.60),
        top_k=3
    )


def test_end_to_end_generation_pipeline(evaluator_instance):
    dataset_path = "day36/mini_project/fixtures/groundedness_evaluation_dataset.json"
    assert Path(dataset_path).exists()

    report = evaluator_instance.run_benchmark(dataset_path)

    assert report.total_scenarios == 15
    assert report.valid_domain_scenarios == 12
    assert report.adversarial_scenarios == 3

    # Bağlama sadakat endüstriyel eşiğin (%75) üzerinde olmalı
    assert report.mean_faithfulness_rate >= 0.75

    # Tuzak ve alan dışı senaryoların tamamında halüsinasyon engellenmeli (%100 Başarı)
    assert report.adversarial_fallback_accuracy == 1.0

    # Alıntı kesinliği yüksek olmalı
    assert report.mean_citation_precision >= 0.80
