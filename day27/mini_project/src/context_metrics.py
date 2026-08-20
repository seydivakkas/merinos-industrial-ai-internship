"""
RAG değerlendirmesi için bağlam (context) metrikleri.
Bu modül, retrieved context'lerin kalitesini ölçmek için
Ragas'ta da kullanılan benzer metriklerin basitleştirilmiş
uygulamalarını içerir.

Temel metrikler:
  - Context Precision: döndürülen context'lerin soruyla
    ne kadar alakalı olduğunu ölçer.
  - Context Recall: gerekli bilgilerin context içinde
    ne kadarının bulunduğunu ölçer.
"""

from typing import List, Dict, Tuple, Any, Optional
import re
import math
from day27.mini_project.src.models import MetricScore
from day27.mini_project.src.claim_extractor import ClaimExtractor


def token_jaccard_similarity(text1: str, text2: str) -> float:
    """
    İki metin arasındaki token tabanlı Jaccard benzerliğini
    hesaplar.
    Args:
        text1: ilk metin
        text2: İkinci metin
    Returns:
        Jaccard benzerlik skoru (0-1 arası)
    """
    tokens1 = set(text1.lower().split())
    tokens2 = set(text2.lower().split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    return intersection / union if union > 0 else 0.0


def extract_numbers_and_units(text: str) -> List[str]:
    """
    Metin içindeki sayıları ve birimleri çıkarır.
    Örn: 120 °C, 5 bar, %100, 30 dakika gibi ifadeler.
    """
    pattern = r"(\d+(?:[.,]\d+)?\s*(?:°C|bar|m3|m³|kg|gr|dakika|mm|rpm|ohm|cn|dtex|c|m|%)?)"
    matches = re.findall(pattern, text.lower())
    result = []
    for m in matches:
        cleaned = m.strip().replace(" ", "")
        if any(char.isdigit() for char in cleaned):
            result.append(cleaned)
    return result


class ContextPrecisionEvaluator:
    """
    Bağlamsal Kesinlik (Context Precision):
    Getirilen bağlam parçalarının ne kadarının gerçekten altın standartla ilgili olduğunu
    ve ilgili parçaların üst sıralarda (rank 1, rank 2) yer alıp almadığını ölçer.
    
    Formül (Average Precision at K):
    Context Precision@K = sum(Precision@k * v_k) / sum(v_k)
    """

    def __init__(self, relevance_threshold: float = 0.28):
        self.relevance_threshold = relevance_threshold

    def is_context_relevant(self, context: str, ground_truth: str, question: str) -> bool:
        """Bağlam parçasının soru ve altın standartla örtüşüp örtüşmediğini belirler."""
        jaccard_gt = token_jaccard_similarity(context, ground_truth)
        jaccard_q = token_jaccard_similarity(context, question)
        combined_score = 0.65 * jaccard_gt + 0.35 * jaccard_q

        # Sayısal ve birimsel teknik örtüşme kontrolü
        gt_nums = set(extract_numbers_and_units(ground_truth))
        ctx_nums = set(extract_numbers_and_units(context))
        num_overlap = len(gt_nums.intersection(ctx_nums)) > 0 if gt_nums else False

        if num_overlap and combined_score >= 0.15:
            return True
        return bool(combined_score >= self.relevance_threshold)

    def evaluate(self, contexts: List[str], ground_truth: str, question: str) -> MetricScore:
        if not contexts:
            return MetricScore(metric_name="context_precision", score=0.0, details={"error": "Boş bağlam listesi"})

        verdicts: List[int] = []
        precisions_at_k: List[float] = []
        relevant_count = 0

        for k, ctx in enumerate(contexts, start=1):
            relevant = self.is_context_relevant(ctx, ground_truth, question)
            verdict = 1 if relevant else 0
            verdicts.append(verdict)
            if verdict == 1:
                relevant_count += 1
            precisions_at_k.append(relevant_count / k)

        total_relevant = sum(verdicts)
        if total_relevant == 0:
            score = 0.0
        else:
            weighted_sum = sum(p * v for p, v in zip(precisions_at_k, verdicts))
            score = float(weighted_sum / total_relevant)

        return MetricScore(
            metric_name="context_precision",
            score=max(0.0, min(1.0, score)),
            details={
                "verdicts": verdicts,
                "precisions_at_k": precisions_at_k,
                "total_contexts": len(contexts),
                "relevant_contexts": total_relevant
            }
        )


class ContextRecallEvaluator:
    """
    Bağlamsal Kapsama (Context Recall):
    Altın standart (ground truth) cevaptaki teknik iddiaların ve sayısal değerlerin
    getirilen bağlam (contexts) tarafından ne oranda kapsandığını ölçer.
    
    Formül:
    Context Recall = (Bağlamda Desteklenen GT İddiaları) / (Toplam GT İddiaları)
    """

    def __init__(self, claim_extractor: Optional[ClaimExtractor] = None, match_threshold: float = 0.25):
        self.extractor = claim_extractor or ClaimExtractor()
        self.match_threshold = match_threshold

    def is_claim_in_contexts(self, claim: str, contexts: List[str]) -> bool:
        """Bir altın standart iddiasının bağlam parçalarında bulunup bulunmadığını denetler."""
        claim_nums = set(extract_numbers_and_units(claim))
        all_context_text = " ".join(contexts)
        all_context_nums = set(extract_numbers_and_units(all_context_text))

        # 1. Sayısal parametre kontrolü: İddiadaki sayılar bağlamların birleşiminde mevcut mu?
        if claim_nums:
            matched_nums = claim_nums.intersection(all_context_nums)
            if not matched_nums:
                return False

        # 2. Bireysel bağlam parçaları üzerinde örtüşme
        for ctx in contexts:
            score = token_jaccard_similarity(claim, ctx)
            ctx_nums = set(extract_numbers_and_units(ctx))
            if claim_nums:
                if len(claim_nums.intersection(ctx_nums)) > 0 and score >= 0.16:
                    return True
            else:
                if score >= self.match_threshold:
                    return True

        # 3. Bağlamların birleşimi üzerinde örtüşme (bilgi birden fazla parçaya dağılmışsa)
        combined_score = token_jaccard_similarity(claim, all_context_text)
        if combined_score >= 0.22:
            return True

        return False

    def evaluate(self, contexts: List[str], ground_truth: str) -> MetricScore:
        gt_claims = self.extractor.extract_claims(ground_truth)
        if not gt_claims:
            return MetricScore(metric_name="context_recall", score=1.0, details={"info": "Altın standartta iddia bulunamadı"})

        supported_flags = []
        for claim in gt_claims:
            is_supported = self.is_claim_in_contexts(claim, contexts)
            supported_flags.append(is_supported)

        supported_count = sum(1 for s in supported_flags if s)
        recall_score = float(supported_count / len(gt_claims))

        return MetricScore(
            metric_name="context_recall",
            score=max(0.0, min(1.0, recall_score)),
            details={
                "total_gt_claims": len(gt_claims),
                "supported_gt_claims": supported_count,
                "claims": gt_claims,
                "supported_flags": supported_flags
            }
        )
