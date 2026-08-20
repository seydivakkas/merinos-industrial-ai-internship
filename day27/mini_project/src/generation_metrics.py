"""
Üretilen cevapların kalitesini değerlendirmek için metrikler.
Bu modül, cevabın kaynak bağlama ne kadar sadık olduğunu
(faithfulness) ve soruyla ne kadar alakalı olduğunu
(answer relevance) ölçmek için değerlendirme sınıflarını
içerir.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import numpy as np
from day27.mini_project.src.models import MetricScore, ClaimItem
from day27.mini_project.src.claim_extractor import ClaimExtractor
from day27.mini_project.src.context_metrics import token_jaccard_similarity, extract_numbers_and_units


class FaithfulnessEvaluator:
    """
    Cevabın verilen context'e ne kadar sadık olduğunu ölçer.
    Halüsinasyon (kaynakta olmayan bilgi) tespiti için
    basit yaklaşımlar kullanılır.
    """

    def __init__(self, claim_extractor: Optional[ClaimExtractor] = None, entailment_threshold: float = 0.28):
        # Sayı, birim ve özel terimleri kontrol etmek için
        # temel kurallar
        self.numeric_pattern = r"\d+(?:[.,]\d+)?"
        self.stopwords = set([
            "ve", "veya", "ile", "için", "bir", "bu", "şu",
            "da", "de", "mi", "mı", "mu", "mü", "olan"
        ])
        self.extractor = claim_extractor or ClaimExtractor()
        self.entailment_threshold = entailment_threshold

    def check_hallucination_indicators(self, answer: str, context: str) -> Dict[str, List[str]]:
        """
        Cevapta bağlamda bulunmayan olası halüsinasyon
        ifadelerini tespit eder.
        """
        indicators = {
            "numbers": [],
            "entities": [],
            "claims": []
        }
        # Cevaptaki sayıları kontrol et
        answer_numbers = re.findall(self.numeric_pattern, answer)
        context_numbers = set(re.findall(self.numeric_pattern, context))
        for num in answer_numbers:
            if num not in context_numbers:
                indicators["numbers"].append(num)
        return indicators

    def is_claim_supported(self, claim: str, contexts: List[str]) -> (bool, Optional[int], float):
        """Bir cevaptaki iddianın bağlam parçaları tarafından desteklenip desteklenmediğini denetler."""
        claim_nums = set(extract_numbers_and_units(claim))
        all_context_text = " ".join(contexts)
        all_context_nums = set(extract_numbers_and_units(all_context_text))

        # 1. Sayısal Halüsinasyon Kontrolü: İddiadaki sayılar bağlamda yoksa kesinlikle desteklenmez
        if claim_nums:
            if not claim_nums.intersection(all_context_nums):
                return False, None, 0.0

        best_score = 0.0
        best_ctx_idx = None

        # 2. Bireysel bağlam parçaları üzerinde arama
        for idx, ctx in enumerate(contexts):
            sim = token_jaccard_similarity(claim, ctx)
            ctx_nums = set(extract_numbers_and_units(ctx))
            
            if claim_nums:
                if len(claim_nums.intersection(ctx_nums)) > 0 and sim >= 0.16:
                    return True, idx, sim
            else:
                if sim >= self.entailment_threshold:
                    return True, idx, sim

            if sim > best_score:
                best_score = sim
                best_ctx_idx = idx

        # 3. Bağlamların birleşimi kontrolü (özellikle birden fazla cümleden beslenen iddialar)
        comb_sim = token_jaccard_similarity(claim, all_context_text)
        if claim_nums and len(claim_nums.intersection(all_context_nums)) > 0 and comb_sim >= 0.20:
            return True, best_ctx_idx, comb_sim
        if not claim_nums and comb_sim >= self.entailment_threshold:
            return True, best_ctx_idx, comb_sim

        return False, best_ctx_idx, best_score

    def evaluate(self, contexts: List[str], answer: str) -> (MetricScore, List[ClaimItem]):
        claims = self.extractor.extract_claims(answer)
        if not claims:
            return MetricScore(metric_name="faithfulness", score=1.0, details={"info": "Cevapta iddia bulunamadı"}), []

        claim_items: List[ClaimItem] = []
        supported_count = 0

        for c_text in claims:
            supported, ctx_idx, sim = self.is_claim_supported(c_text, contexts)
            if supported:
                supported_count += 1
            claim_items.append(
                ClaimItem(
                    claim_text=c_text,
                    supported=supported,
                    evidence_context_idx=ctx_idx,
                    similarity_score=round(sim, 4)
                )
            )

        faithfulness_score = float(supported_count / len(claims))

        score_obj = MetricScore(
            metric_name="faithfulness",
            score=max(0.0, min(1.0, faithfulness_score)),
            details={
                "total_claims": len(claims),
                "supported_claims": supported_count,
                "unsupported_claims": len(claims) - supported_count
            }
        )
        return score_obj, claim_items


class AnswerRelevanceEvaluator:
    """
    Cevap Uygunluğu (Answer Relevance):
    Üretilen cevabın kullanıcının sorduğu teknik soru ile doğrudan alakalı olup olmadığını,
    konudan sapıp sapmadığını veya gereksiz tekrar yapıp yapmadığını ölçer.
    """

    def __init__(self, claim_extractor: Optional[ClaimExtractor] = None, relevance_threshold: float = 0.20):
        self.extractor = claim_extractor or ClaimExtractor()
        self.relevance_threshold = relevance_threshold

    def evaluate(self, question: str, answer: str) -> MetricScore:
        claims = self.extractor.extract_claims(answer)
        if not claims:
            return MetricScore(metric_name="answer_relevance", score=0.0, details={"error": "Boş cevap"})

        relevance_scores = []
        q_keywords = set(re.findall(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}\b", question.lower()))

        for c in claims:
            sim = token_jaccard_similarity(c, question)
            c_keywords = set(re.findall(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}\b", c.lower()))
            kw_overlap = len(q_keywords.intersection(c_keywords)) / max(1, len(q_keywords))
            
            combined = 0.45 * sim + 0.55 * kw_overlap
            relevance_scores.append(combined)

        raw_avg = float(sum(relevance_scores) / len(relevance_scores))
        
        # Normalizasyon: 0.15 ve üzeri yüksek alaka
        normalized_score = min(1.0, raw_avg / 0.28)
        if raw_avg < 0.05:
            normalized_score = 0.0

        return MetricScore(
            metric_name="answer_relevance",
            score=max(0.0, min(1.0, normalized_score)),
            details={
                "raw_average_sim": round(raw_avg, 4),
                "num_claims": len(claims),
                "relevance_scores": [round(s, 4) for s in relevance_scores]
            }
        )
