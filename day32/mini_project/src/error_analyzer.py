# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 32
Error Analyzer: Hata Taksonomisi ve Teşhis Analiz Motoru
(KEYWORD_MISMATCH, CODE_DRIFT, CHUNK_BOUNDARY, OUT_OF_DOMAIN)
"""

from typing import List, Dict, Optional
from day32.mini_project.src.models import (
    GoldenQuery,
    SystemEvaluationReport,
    QueryEvaluationResult,
    ErrorRecord
)


class ErrorAnalyzer:
    """
    Retrieval motorunun başarısız olduğu veya hedefi 1. sıraya getiremediği
    durumları sınıflandıran ve somut mühendislik aksiyonları öneren teşhis motoru.
    """

    def __init__(self):
        pass

    def diagnose_query_failure(
        self,
        system_name: str,
        query: GoldenQuery,
        result: QueryEvaluationResult
    ) -> Optional[ErrorRecord]:
        """Tek bir sorgu sonucunu analiz ederek hata kaydı üretir."""
        # 1. Alan Dışı (Negative Control) Sorgu Kontrolü
        if query.category == "OUT_OF_DOMAIN":
            return ErrorRecord(
                query_id=query.id,
                query=query.query,
                category=query.category,
                system_name=system_name,
                failure_type="OUT_OF_DOMAIN",
                expected_target="YOK (Negatif Kontrol)",
                actual_top1=result.top1_retrieved_chunk_id,
                target_rank=None,
                explanation="Sorgu, fabrika SOP ve üretim kılavuzları dışında genel idari bir konudur. Korpus bu bilgiyi içermez.",
                recommendation="Arama motoruna minimum benzerlik skoru eşiği (Threshold Gate) eklenerek bu tip sorgular 'Bilgi Bulunamadı' olarak filtrelenmelidir."
            )

        # 2. Eğer hedef 1. sırada doğru geldiyse hata yoktur
        if result.top1_correct:
            return None

        # 3. Hata türünü belirle
        target_rank = result.found_rank
        actual_top1 = result.top1_retrieved_chunk_id

        # A. Kod Sapması (CODE_DRIFT): Sorguda teknik kod veya sayısal eşik var ama model kaçırmış
        has_code = any(kw.startswith("E-") or "bar" in kw or "Newton" in kw or "80x" in kw or "28 tel" in kw for kw in query.keywords)
        if query.category == "EXACT_CODE" or has_code:
            if "Dense" in system_name:
                failure_type = "CODE_DRIFT"
                explanation = f"Yoğun vektörel embedding, '{', '.join(query.keywords)}' gibi kritik teknik kodları genel anlamsal uzayda seyreltti ve 1. sırayı kaçırdı (Sıra: {target_rank})."
                recommendation = "BM25 leksikal arama ağırlığı artırılmalı veya RRF füzyonu kullanılarak leksikal kesinlik korunmalıdır."
            else:
                failure_type = "KEYWORD_MISMATCH"
                explanation = f"Sorgu terimleri ile parça terimleri arasında leksikal uyumsuzluk oluştu (Hedef Sıra: {target_rank})."
                recommendation = "Metin temizleme adımında teknik kodların ayrışması engellenmeli veya chunk başlık hiyerarşisi (breadcrumbs) güçlendirilmelidir."

        # B. Leksikal Eşleşmeme (KEYWORD_MISMATCH): Doğal dil semptom sorgusunda BM25 başarısızlığı
        elif query.category == "SEMANTIC_SYMPTOM":
            if "BM25" in system_name:
                failure_type = "KEYWORD_MISMATCH"
                explanation = f"Operatörün kullandığı doğal dil ifadeleri, belgedeki teknik terimlerle birebir örtüşmediği için Okapi BM25 hedefi 1. sıraya getiremedi (Sıra: {target_rank})."
                recommendation = "Dense (SentenceTransformer) vektörel anlamsal getirme devreye alınmalı veya eşanlamlılar tablosu (synonym mapping) tanımlanmalıdır."
            else:
                failure_type = "CHUNK_BOUNDARY"
                explanation = f"Sorgu anlamsal olarak doğru yönlendirildi ancak parça içi bağlam penceresi yetersiz kaldığından hedef geriye düştü (Sıra: {target_rank})."
                recommendation = "Chunk boyutu veya parça örtüşme (overlap) oranı artırılmalıdır."

        # C. Hibrit Karmaşık Sorgu (CHUNK_BOUNDARY veya RANK_DILUTION)
        else:
            failure_type = "CHUNK_BOUNDARY"
            explanation = f"Hibrit sorguda hedef bilgi parça sınırları arasında kaldı veya komşu parçalar daha yüksek skor aldı (Sıra: {target_rank})."
            recommendation = "Anlamsal yapısal parçalayıcı (SemanticStructureChunker) ile başlık-paragraf bütünlüğü korunmalıdır."

        return ErrorRecord(
            query_id=query.id,
            query=query.query,
            category=query.category,
            system_name=system_name,
            failure_type=failure_type,
            expected_target=query.target_chunk_id,
            actual_top1=actual_top1,
            target_rank=target_rank,
            explanation=explanation,
            recommendation=recommendation
        )

    def analyze_report(
        self,
        report: SystemEvaluationReport,
        queries: List[GoldenQuery]
    ) -> List[ErrorRecord]:
        """Verilen sistem raporundaki tüm hataları tespit ve analiz eder."""
        q_map = {q.id: q for q in queries}
        records: List[ErrorRecord] = []

        for res in report.results:
            q = q_map.get(res.query_id)
            if q:
                err = self.diagnose_query_failure(report.system_name, q, res)
                if err:
                    records.append(err)

        return records

    def compare_system_failures(
        self,
        reports: Dict[str, SystemEvaluationReport],
        queries: List[GoldenQuery]
    ) -> Dict[str, Dict[str, int]]:
        """Sistemler arası hata kategorisi sıklık tablosunu çıkarır."""
        stats: Dict[str, Dict[str, int]] = {}
        for sname, rep in reports.items():
            errs = self.analyze_report(rep, queries)
            cat_counts: Dict[str, int] = {
                "KEYWORD_MISMATCH": 0,
                "CODE_DRIFT": 0,
                "CHUNK_BOUNDARY": 0,
                "OUT_OF_DOMAIN": 0
            }
            for e in errs:
                if e.failure_type in cat_counts:
                    cat_counts[e.failure_type] += 1
            stats[sname] = cat_counts
        return stats
