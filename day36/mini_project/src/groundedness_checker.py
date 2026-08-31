# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 36
Groundedness Checker: Atomik İddia Ayrıştırma, NLI Doğrulama ve Alıntı Metrikleri
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from day31.mini_project.src.models import ChunkRecord
from day36.mini_project.src.models import (
    StructuredAnswer,
    ClaimVerificationResult,
    GroundednessMetric
)


def _normalize_tokens(text: str) -> set:
    """Türkçe karakterleri ASCII eşleniklerine normalize ederek token kümesi üretir."""
    norm = text.lower().translate(str.maketrans("ığüşöçâîû", "igusocaiu"))
    return set(re.findall(r"\b\w{3,}\b", norm))


class GroundednessChecker:
    """
    Üretilen yanıtın bağlama sadakatini (Faithfulness) ve
    alıntıların doğruluğunu (Citation Precision / Recall) denetleyen katı doğrulayıcı.
    """

    def __init__(self, threshold: float = 0.50):
        self.threshold = threshold

    def extract_claims(self, answer: Any) -> List[str]:
        """Yapılandırılmış yanıttan bağımsız iddia cümlelerini ayrıştırır."""
        direct_ans = getattr(answer, "answer", getattr(answer, "direct_answer", ""))
        steps = getattr(answer, "steps", getattr(answer, "action_steps", []))
        fallback = getattr(answer, "fallback_triggered", False)

        if fallback:
            return [direct_ans]

        claims = []
        # Ondalıklı sayıları (0.45 gibi) bölmeden cümlelere ayrıştır
        d_sentences = [s.strip() for s in re.split(r"(?<!\d)\.(?!\d)|\n", direct_ans) if len(s.strip()) > 8]
        claims.extend(d_sentences)

        for step in steps:
            s_clean = step.strip()
            if len(s_clean) > 8 and s_clean not in claims:
                claims.append(s_clean)

        return claims if claims else [direct_ans]

    def verify_claim(self, claim: str, context_chunks: List[Any], cited_chunk_id: Optional[str] = None) -> ClaimVerificationResult:
        """Tek bir iddianın bağlam tarafından desteklenip desteklenmediğini NLI mantığıyla test eder."""
        target_chunks = context_chunks
        if cited_chunk_id:
            specific = [c for c in context_chunks if (c.get("chunk_id") if isinstance(c, dict) else getattr(c, "chunk_id", None)) == cited_chunk_id]
            if specific:
                target_chunks = specific

        claim_tokens = _normalize_tokens(claim)
        if not claim_tokens:
            return ClaimVerificationResult(
                claim_text=claim,
                cited_chunk_id=cited_chunk_id,
                is_supported=True,
                similarity_score=1.0,
                verdict="FAITHFUL"
            )

        best_score = 0.0
        best_chunk_id = None

        for chunk in target_chunks:
            c_text = chunk.get("text", "") if isinstance(chunk, dict) else getattr(chunk, "text", "")
            c_id = chunk.get("chunk_id", "") if isinstance(chunk, dict) else getattr(chunk, "chunk_id", "")
            chunk_tokens = _normalize_tokens(c_text)

            matched_count = 0
            for ct in claim_tokens:
                if ct in chunk_tokens:
                    matched_count += 1
                elif len(ct) >= 4 and any((other.startswith(ct[:4]) or ct.startswith(other[:4])) for other in chunk_tokens if len(other) >= 4):
                    matched_count += 1
            score = matched_count / len(claim_tokens)

            # Sayısal değer veya hata kodu kontrolü
            claim_nums = set(re.findall(r"\b\d+(?:\.\d+)?\b|E-\d{3}", claim))
            chunk_nums = set(re.findall(r"\b\d+(?:\.\d+)?\b|E-\d{3}", c_text))
            num_match = claim_nums.issubset(chunk_nums) if claim_nums else True

            if score > best_score and num_match:
                best_score = score
                best_chunk_id = c_id

        is_supported = (best_score >= self.threshold)
        verdict = "FAITHFUL" if is_supported else "UNSUPPORTED"

        return ClaimVerificationResult(
            claim_text=claim,
            cited_chunk_id=best_chunk_id or cited_chunk_id,
            is_supported=is_supported,
            similarity_score=round(best_score, 4),
            verdict=verdict
        )

    def evaluate_answer(self, answer: Any, context_chunks: List[Any]) -> Tuple[GroundednessMetric, List[ClaimVerificationResult]]:
        """Bir yanıtın tüm iddialarını ve alıntılarını uçtan uca değerlendirir."""
        fallback = getattr(answer, "fallback_triggered", False)
        direct_ans = getattr(answer, "answer", getattr(answer, "direct_answer", ""))
        citations = getattr(answer, "citations", [])

        if fallback:
            metric = GroundednessMetric(
                total_claims=1,
                supported_claims=1,
                faithfulness_rate=1.0,
                citation_precision=1.0,
                citation_recall=1.0
            )
            res = [
                ClaimVerificationResult(
                    claim_text=direct_ans,
                    cited_chunk_id=None,
                    is_supported=True,
                    similarity_score=1.0,
                    verdict="FAITHFUL"
                )
            ]
            return metric, res

        claims = self.extract_claims(answer)
        verification_results: List[ClaimVerificationResult] = []
        supported_count = 0

        primary_cited_chunk = citations[0].chunk_id if citations else None

        for claim in claims:
            v_res = self.verify_claim(claim, context_chunks, cited_chunk_id=primary_cited_chunk)
            verification_results.append(v_res)
            if v_res.is_supported:
                supported_count += 1

        total_claims = len(claims)
        faithfulness = round(supported_count / total_claims, 4) if total_claims > 0 else 0.0

        # Alıntı Hassasiyeti (Citation Precision)
        valid_citations = 0
        total_citations = len(citations)

        chunk_dict = {}
        for c in context_chunks:
            cid = c.get("chunk_id", "") if isinstance(c, dict) else getattr(c, "chunk_id", "")
            ctxt = c.get("text", "") if isinstance(c, dict) else getattr(c, "text", "")
            chunk_dict[cid] = ctxt

        for cit in citations:
            if cit.chunk_id in chunk_dict:
                c_text = chunk_dict[cit.chunk_id]
                c_tokens = _normalize_tokens(c_text)
                quote_text = getattr(cit, "quote", "") or ""
                q_tokens = _normalize_tokens(quote_text)
                if not q_tokens or len(q_tokens.intersection(c_tokens)) / len(q_tokens) >= 0.4:
                    valid_citations += 1

        citation_prec = round(valid_citations / total_citations, 4) if total_citations > 0 else 1.0
        claims_with_citation = supported_count if total_citations > 0 else 0
        citation_rec = round(claims_with_citation / total_claims, 4) if total_claims > 0 else 0.0

        metric = GroundednessMetric(
            total_claims=total_claims,
            supported_claims=supported_count,
            faithfulness_rate=faithfulness,
            citation_precision=citation_prec,
            citation_recall=citation_rec
        )

        return metric, verification_results
